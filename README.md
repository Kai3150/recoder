This program create abstraction paper of meetings



python -m spacy download ja_core_news_sm
python -m spacy download ja_core_news_md


recoder.pyの処理並列化についての指針

・ホストPCで動画データをネットワーク内の処理可能なPC分に分割する。ただし最小サイズは守る。
・分割されたmp3を配布
・各PCで文字起こし処理を行う。
・出力されたテキストを前処理する。(できるとこまでで良い)
・前処理されたテキストを順番を揃えてホストPCに集計
・全て集まったら、全体を通して前処理を行う。
・(重要単語を抽出しWikipediaに問い合わせる。)(無駄な単語を問い合わせる可能性があるのでホスト側でするべき)
・htmlに出力する。
・できたファイルをネットワークのPCに配布して終了



アプリの流れ

web版
js内
WebAssemblyでjsからGOを呼び出す。
   https://www.asobou.co.jp/blog/web/go-webassembly-3
    or
    js-p2plibでなんとかする。(NAT traversalがうまくできない可能性が有る)

    libp2pで近くのnodeとコネクションを確立する。
    最新の情報を確認する。
    最新の情報がない場合:
        ホストにある場合:
            ホストに要求する。
        ホストにない場合:
            自分がホストとなり議事録作成プログラムの実行を始めることができる
                python  "file name"  ->  "file" or "dict like object"
                https://poweruser.blog/embedding-python-in-go-338c0399f3d5

    議事録のhtmlファイルをjsに返す。
出力

　　|
　　|  PWA化(https://qiita.com/poster-keisuke/items/6651140fa20c7aa18474)
　　|
   \/

アプリ版


テストのすべきこと
goでコネクションを確立して他ノードで受け取ったデータを引数にした関数を呼び出しホストに結果を返す。

goの関数をpythonスクリプトに置き換える。
