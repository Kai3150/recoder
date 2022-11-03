var pc = new webkitRTCPeerConnection(servers,
    { optional: [{ RtpDataChnnels: true }] });

pc.ondatachannel = function (event) {
    receiveChannel = event.channel;
    receiveChannel.onmessage = function (event) {
        document.querySelector("div#receive").innerHTML = event.data;
    };
};

sendChannel = pc.createDataChannel('sendDataChannel', { reliable: false });

document.querySelector('button#send').onclick = function () {
    var data = document.querySelector('textarea#send').value;
    sendChannel.send(data);
}
