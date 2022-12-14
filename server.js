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
        console.log('in the /api/v1/imgs error');
        console.log(error);
    }
})

app.get('/', function (req, res, next) {
    const ua = req.headers['user-agent'].toLowerCase();

    if (/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(ua) || /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(ua.substr(0, 4))) {
        res.sendFile(path.join(__dirname, 'output/public/top/slide.html'));
    } else if (ua.indexOf('chrome') != -1){
        res.sendFile(path.join(__dirname, 'output/public/top/index.html'));
    } else if (ua.indexOf("safari") != -1) {
        res.sendFile(path.join(__dirname, 'output/public/top/slide.html'));
    } else {
        res.sendFile(path.join(__dirname, 'output/public/top/index.html'));
    }
})

app.get('/index.html', function (req, res, next) {
    res.sendFile(path.join(__dirname, 'output/public/top/index.html'));
})

app.get('/slide.html', function (req, res, next) {
    res.sendFile(path.join(__dirname, 'output/public/top/slide.html'));
})

app.get('output.mp3', function (req, res, next) {
    res.sendFile(path.join(__dirname, 'python/audio/output.mp3'));
})

// get img????????????
app.get("/api/files", async (req, res) => {
    try {
        const existfiles = [];
        fs.readdir('output/public/gijiroku', (err, files) => {
            files.reverse()
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

//post ????????????
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
        console.log('in the /upload error');
        console.log(error);
    }
})

let server = app.listen(process.env.PORT || 3000, '0.0.0.0',function () {
    console.log("listening at port localhost:%s", server.address().port);
});

// ???????????????????????????
// [????????????????????????] > [??????????????????] > [??????] > [TCP / IP]
// 192.168.10.101:3000/#/3
// ??????????????????
