const mongoose = require("mongoose");

const ThreadSchema = new mongoose.Schema({
    htmlName: {
        type: String,
        required: true,
        maxlength: 20,
    },
    imgName: {
        type: String,
        required: true,
    },
    imgType: {
        type: String,
        required: true,
    }
});

module.exports = mongoose.model('Thread', ThreadSchema);
