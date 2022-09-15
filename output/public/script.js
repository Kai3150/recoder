const inputTextDOM = document.getElementById("inputTitle");
const inputContentDOM = document.getElementById("inputContent");
//formDomを追加する。
const formDOM = document.querySelector(".form-section");
const threadSectionDOM = document.querySelector(".thread-section");
const formDom2 = document.querySelector('.form-img');

let inputText = "";
let contentText = "";

//最初はThreadを全て読み込む
const getAllThreads = async () => {
    try {
        console.log("show");
        let allThreads = await axios.get("/api/v1/threads");
        console.log(allThreads);
        let { data } = allThreads;
        //出力
        allThreads = data
            .map((thread) => {
                const { title, content } = thread;
                console.log(title);
                return `
      <div class="single-thread">
          <h3>${title}</h3>
          <p>${content}</p>
        </div>
      `;
            })
            .join("");
        //挿入
        threadSectionDOM.innerHTML = allThreads;
    } catch (err) {
        console.log(err);
    }
};

//getAllThreads();


// htmlファイルの名前 -> そのファイルのimgの名前
const getImages = async () => {
    try {
        console.log("in the get Images");
        let imgs = await axios.get("/api/v1/imgs", {
            params: {
                // ファイル名をつける
                htmlName: window.location.href.split('/').pop()
            }
        });
        console.log(imgs);
        let { data } = imgs;
        //出力
        imgs = data
            .map((img) => {
                const { htmlName, imgName, imgType } = img;
                console.log(imgName);
                return `<img src="${imgNamë}" >`;
            })
            .join("");
        //挿入
        threadSectionDOM.innerHTML = allThreads;
    } catch (err) {
        console.log(err);
    }
};

getImages()

//タイトルと内容を打ち込んだらpostメソッドを実装してデータ追加。
inputTextDOM.addEventListener("change", (e) => {
    //   console.log(e.target.value);
    inputText = e.target.value;
});
inputContentDOM.addEventListener("change", (e) => {
    contentText = e.target.value;
});

formDOM.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (inputText && inputContent) {
        console.log("success");
        //postメソッドで送信する。

        try {
            console.log(inputText);
            await axios.post("/api/v1/thread", {
                title: inputText,
                content: contentText,
            });
            getAllThreads();
        } catch (err) {
            console.log(err);
        }

        //投稿したらinputのvalueを削除
        inputText = "";
        contentText = "";
        inputTextDOM.value = "";
        inputContentDOM.value = "";
    } else {
        console.log("error");
    }
});
