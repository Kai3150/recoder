pc = new RTCPeerConnection(null);
pc.onaddstream = gotRemoteStream;
//pc.addstream(localStream);
pc.createOffer(gotOffer);

function gotOffer(desc) {
    pc.setLocalDescription(desc);
    sendOffer(desc);
}

function gotAnswer(desc) {
    pc.setRemoteDescription(desc);
}

function gotRemoteStream(e) {
    attachMediaStream(remoteVideo, e.stream)
}

console.log(pc);
