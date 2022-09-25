const dropZone = document.getElementById('drop-zone');
const preview = document.getElementById('preview');
const uploaded = document.getElementById('uploaded');

const fileInput = document.getElementById('file-input');
//formDomを追加する。
const formDOM = document.querySelector(".form-img");

let imgName;
const htmlName = window.location.href.split('/').pop();
let imgType;


dropZone.addEventListener('dragover', function (e) {
    e.stopPropagation();
    e.preventDefault();
    this.style.background = '#e1e7f0';
}, false);

dropZone.addEventListener('dragleave', function(e) {
    e.stopPropagation();
    e.preventDefault();
    this.style.background = '#ffffff';
    console.log('in the leave');
}, false);

fileInput.addEventListener('change', function (e) {
    console.log('in  the change');
    e.preventDefault();
    previewFile(this.files[0]);
});

dropZone.addEventListener('drop', function(e) {
    e.stopPropagation();
    e.preventDefault();
    //this.style.background = '#ffffff'; //背景色を白に戻す
    let files = e.dataTransfer.files; //ドロップしたファイルを取得
    //console.log(files);
    preview.innerHTML = '';

    //if (files.length > 1) return alert('アップロードできるファイルは1つだけです。');
    fileInput.files = files; //inputのvalueをドラッグしたファイルに置き換える。
    const len = 100 / files.length;

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        //previewFile(file)//の置き換え
        let fr = new FileReader();
        fr.readAsDataURL(file);
        fr.onload = function () {
            let img = document.createElement('img');
            img.setAttribute('src', fr.result);
            img.style.width = `${len}%`;
            preview.appendChild(img);
        };
        //previewFile終わり
        imgName = file.name;
    }
}, false);


formDOM.addEventListener("submit", async (e) => {
    imgType = "bansho";

    e.preventDefault();
    const files = fileInput.files;
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }

    const action = formDOM.getAttribute("action")
    const options = {
        method: 'POST',
        headers: new Headers({
            "htmlname": htmlName,
            "imgname": imgName,
            "imgtype": imgType
        }),
        body: formData,
    }
    formDOM.reset();
    await fetch(action, options).then((e) => {
        if (e.status === 200) {
            alert("保存しました。")
            return
        }
        alert("保存できませんでした。")
    })
    preview.innerHTML = "";
    getImages2();
});

function previewFile(file) {
    /* FileReaderで読み込み、プレビュー画像を表示。 */
    let fr = new FileReader();
    fr.readAsDataURL(file);
    fr.onload = function() {
        let img = document.createElement('img');
        img.setAttribute('src', fr.result);
        //img.style.width = ''
        preview.appendChild(img);
    };
}

// htmlファイルの名前 -> そのファイルのimgの名前
const getImages = async () => {
    try {
        let imgs = await axios.get("/api/v1/imgs", {
            params: {
                // ファイル名をつける
                htmlName: window.location.href.split('/').pop()
            }
        });

        let { data } = imgs;
        //出力
        imgs = data.map((img) => {
                const { htmlName, imgName, imgType } = img;
                return `<img src="/uploads/${imgName}" >`;
            })
            .join("");
        //挿入
        preview.innerHTML = imgs;
    } catch (err) {
        console.log(err);
    }
};

const getImages2 = async () => {
    const action = formDOM.getAttribute("action")
    const options = {
        method: 'GET',
        headers: new Headers({"htmlname": htmlName,})
    }

    fetch("/api/v1/imgs", options)
    .then(imgs => {
        return imgs.json();
    }).then(post => {
        //出力
        const len = 100 / post.length;
        uploaded.innerHTML = '';
        imgs = post.map((img) => {
            const { htmlName, imgName, imgType } = img;
            const imgel = document.createElement('img');
            imgel.setAttribute('src', `/uploads/${imgName}`);
            imgel.style.width = `${len}%`;
            uploaded.appendChild(imgel);
        });
    });
};
getImages2();
