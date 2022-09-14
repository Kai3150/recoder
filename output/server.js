const express = require('express');
const path = require('path');
const multer = require('multer');

const app = express();

const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, 'public/uploads/')
    },
    filename: function (req, file, cb) {
        cb(null, file.originalname)
    }
})
const upload = multer({ storage: storage })

app.use(express.static(path.join(__dirname, 'public')))

app.get('/', (req, res) => res.sendFile(path.join(__dirname, 'sample.html')))
app.get('/sample.html', (req, res) => res.sendFile(path.join(__dirname, 'sample.html')))
app.get('/upload.html', (req, res) => res.sendFile(path.join(__dirname, 'public/upload.html')))

app.get('/style.css', (req, res) => res.sendFile(path.join(__dirname, 'style.css')))
app.get('/wikipedia-preview.development.js', (req, res) => res.sendFile(path.join(__dirname, 'wikipedia-preview.development.js')))
app.get('/file.js', (req, res) => res.sendFile(path.join(__dirname, 'file.js')))

app.post('/upload', upload.single('file'), function (req, res, next) {
    res.send('ファイルのアップロードが完了しました。');
})

var server = app.listen(3000, function () {
    console.log("listening at port %s", server.address().port);
});
