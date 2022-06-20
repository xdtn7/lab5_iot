function send_data () {
    serial.writeString("!1:LIGHT:" + input.lightLevel() + "#")
    basic.pause(1000)
}
input.onButtonPressed(Button.A, function () {
    mqtt_data_available = 1
})
function send_ack () {
    radio.sendString("ACK 200 OK")
    serial.writeString("!1:ACK:200#")
}
function statemachine () {
    switch (current_state) {
        case STATE['IDLE']:
            basic.showString("I")
            // if (counter == 2) {
            //     mqtt_data_available = 1;
            //     counter = 0;
            // }
            // else counter++;
            
            if (mqtt_data_available) {
                current_state = STATE['SEND DATA']
                mqtt_data_available = 0
            }
            else if (serial_data_available) {
                current_state = STATE['SEND ACK'];
                serial_data_available = 0
            }
            break;
        case STATE['SEND ACK']:
            basic.showString("A")
            send_ack();
            current_state = STATE['IDLE'];
            break;
        case STATE['SEND DATA']:
            basic.showString("D")
            send_data();
            current_state = STATE['WAIT ACK'];
            break;
        case STATE['WAIT ACK']:
            basic.showString("W")
            if(counter==2) time_flag = 1 
            if (ack_receive_successful) {
                current_state = STATE['IDLE'];
                counter = 0;
                ack_receive_successful = 0;
            }
            else if (counter_failure < MAX) {
                if (time_flag) {
                    current_state = STATE['SEND DATA'];
                    counter = 0
                    time_flag = 0
                    counter_failure++
                }
                else counter++;
            }
            else if (counter_failure >= MAX) {
                current_state = STATE['ERROR LOG'];
                
            }
            break;
        case STATE['ERROR LOG']:
            basic.showString("E")
            // basic.showString("Error log!")
            counter_failure = 0
            current_state = STATE['IDLE'];
            break;

    }
}
// if (cmd == "0") {
// LED = 0
// basic.showLeds(`
// . # # # .
// # # . # #
// # # . # #
// # # . # #
// . # # # .
// `)
// } else if (cmd == "1") {
// LED = 1
// basic.showLeds(`
// . . # . .
// . # # . .
// . . # . .
// . . # . .
// # # # # #
// `)
// } else if (cmd == "2") {
// FAN = 2
// basic.showLeds(`
// # # # # .
// . . . . #
// # # # # #
// # . . . .
// . # # # #
// `)
// } else if (cmd == "3") {
// FAN = 3
// basic.showLeds(`
// # # # # .
// . . . # .
// . # # # #
// . . . # .
// # # # # .
// `)
// }
serial.onDataReceived(serial.delimiters(Delimiters.Hash), function () {
    cmd = serial.readUntil(serial.delimiters(Delimiters.Hash))
    // basic.showString(cmd)
    if (cmd == "ACK") {
        ack_receive_successful = 1
    } else {
        serial_data_available = 1
    }
})
let cmd = ""
let serial_data_available = 0
let mqtt_data_available = 0
let time_flag = 0
let counter = 0
let ack_receive_successful = 0
let counter_failure = 0
let current_state = 0
let LED = -1
let FAN = -1
let MAX = 5
const STATE = {
    'IDLE': 0,
    'SEND ACK': 1,
    'SEND DATA': 2,
    'WAIT ACK': 3,
    'ERROR LOG': 4
}
radio.setGroup(57)
basic.forever(function () {
    statemachine()
    basic.pause(1000)
})
