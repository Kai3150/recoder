const express = require('express');
const path = require('path');
const multer = require('multer');
const mongoose = require("mongoose");
const bodyParser = require("body-parser");
const app = express();
const Thread = require("./output/models/Thread");

app.use(express.json());
app.use(express.static(path.join(__dirname, 'output/public')));
app.use(bodyParser.urlencoded({ extended: true }));

const fs = require('fs');



mongoose.connect("mongodb+srv://kai:Kkkh3150@cluster0.4mb3bi1.mongodb.net/?retryWrites=true&w=majority")
    .then(() => console.log('DB connected'))
    .catch((err) => console.log(err));


app.get("/api/v1/imgs", async (req, res) => {
    try {
        const imgs = await Thread.find({ htmlName: req.headers.htmlname });
        res.status(200).json(imgs);
    } catch (error) {
        console.log(error);
    }
})

app.get('/', function (req, res, next) {
    res.sendFile(path.join(__dirname, 'output/public/top/index.html'));
})

app.get('/index.html', function (req, res, next) {
    res.sendFile(path.join(__dirname, 'output/public/top/index.html'));
})

// get imgメソッド
app.get("/api/files", async (req, res) => {

    try {
        const existfiles = [];
        fs.readdir('output/public/gijiroku', (err, files) => {
            files.forEach(file => {
                if (file.includes('.html')) { existfiles.push(file) }
            });
            res.json({ ...existfiles });
        });

    } catch (error) {
        console.log('error');
    }
})

const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, 'output/public/uploads/');
    },
    filename: function (req, file, cb) {
        cb(null, file.originalname);
    }
})
const upload = multer({ storage: storage });

//post メソッド
app.post('/upload', upload.array('files'), async (req, res, next) => {
    let search = [];
    req.files.forEach(file => {
        search.push({
            htmlName: req.headers.htmlname,
            imgName: file.originalname,
            imgType: req.headers.imgtype
        })
    });
    try {
        const createThread = await Thread.create(search);
        res.status(200).json(createThread);
        console.log('new create');
    } catch (error) {
        res.status(200).json({});
        console.log(error);
    }
})

let server = app.listen(process.env.PORT || 3000, function () {
    console.log("listening at port %s", server.address().port);
});
