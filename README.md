# Inventor portfolio — Tung-Ming Yu

靜態個人作品集：ITRI 專利、論文、Somnics 發明（公開紀錄）。無後端、無框架、無 npm；只需 Python 3。

## 目錄

```
patent-site/
├── build.py               讀 data/*.json → 產出下列 HTML/CSS/JS
├── data/
│   ├── site.json          姓名、一句話定位、外部連結（LinkedIn / Scholar / ORCID）、時間軸
│   ├── patents.json       專利家族（itri / somnics 兩組）、領域、角色、國別對照
│   └── publications.json  期刊與研討會論文（含 DOI、Crossref 引用數）
├── index.html             首頁
├── itri.html              ITRI 專利（10 家族）
├── publications.html      論文（8 篇）
├── somnics.html           Somnics 發明（6 家族，僅公開紀錄欄位）
├── style.css / app.js     由 build.py 產生
└── README.md
```

## 更新內容

1. 改 `data/*.json`（不要直接改 HTML，重建會被覆蓋）。
2. `python build.py`
3. commit + push，GitHub Pages 約一分鐘後更新。

新增專利：在對應的 `families` 陣列加一個物件，`pubs` 內每件公告填 `pn`（Google Patents 用的公告號含 kind code，例如 `US11712363B2`）。Google Patents 不收錄的號碼（VN、部分 SG、TW 設計專利）加 `"link": false`。

## 部署到 GitHub Pages

```powershell
cd D:\linkedin\patent-site
git init
git add .
git commit -m "Inventor portfolio site"
# 在 GitHub 建一個 repo，名稱建議 <username>.github.io（網址最乾淨）或 patents
git remote add origin https://github.com/<username>/<repo>.git
git branch -M main
git push -u origin main
```

GitHub → repo → **Settings → Pages → Source: Deploy from a branch → main / (root)**。
網址會是 `https://<username>.github.io/` 或 `https://<username>.github.io/<repo>/`。

## 自訂網域（已設定：patents.aurorixa.com）

- repo 根目錄的 `CNAME` 檔內容是 `patents.aurorixa.com`——**不要刪**，GitHub 靠它記住網域設定。
- DNS（aurorixa.com 的管理面板）：`CNAME  patents  →  arkep96g-eng.github.io`
- GitHub → Settings → Pages → Custom domain 填 `patents.aurorixa.com` → DNS check 通過後勾 Enforce HTTPS。
- 換網域時同步改 `data/site.json` 的 `base_url`，並重跑 `python make_og.py` 更新預覽圖上的網址。

## 預覽圖

`python make_og.py` 產生 `assets/og.png`（1200×630，LinkedIn / X 分享卡片）。數字從 data/*.json 計算，改資料後重跑。

## 發布前填入

`data/site.json` → `links`：

- `linkedin`：你的公開 profile 網址（LinkedIn → Me → View profile → 網址列）
- `scholar`：Google Scholar profile（若尚未建立：scholar.google.com → My profile，加入 8 篇論文後引用數會自動更新）
- `orcid`：ORCID iD（orcid.org 免費註冊）

空字串的連結不會顯示。

## LinkedIn 對應

| 位置 | 做法 |
|---|---|
| **先關通知** | Settings & Privacy → Visibility → *Share profile updates with your network* → Off。否則每加一筆專利／論文，所有聯絡人都會收到通知。 |
| Contact info → Website | 類型 *Portfolio*，貼首頁網址。可再加一個 *Other* 標「Google Scholar」。 |
| Featured | *Add link* → 首頁網址。一張卡就好。 |
| About 結尾 | 一行 `Full patent & publication portfolio: <網址>` |
| Patents（Add profile section → Additional → Patents） | 每筆填：Title、Patent office、Patent/application number、Inventors（可 tag 有 LinkedIn 的共同發明人）、Issue date、URL。URL 指向 `itri.html#<family id>` 或 `somnics.html#<family id>`（id 見 `patents.json`）。建議先填：US8216196B2（sole）、US7682827B2（sole）、US8616208B2、US11712363B2、US10166140B2、TWM557616U（first）。 |
| Publications | 5 篇期刊逐筆填，URL 用 `https://doi.org/<DOI>`；Optics Letters 2010（95 次引用）與 Sens. Actuators B 2013（第一作者）優先。 |
| Licenses & certifications | LabVIEW 基礎認證（NI）、WBSA 初階商務企劃員。不放網站。 |

## 資料來源與已排除項目

- 專利發明人身分已於 2026-09-17 逐件與 Google Patents 核對；DOI 與引用數來自 Crossref。
- **未收錄**：Somnics 全公司其他專利（非本人發明）、`P07TH`（泰國，Pending 未公開）、`US10462860B2`（Elite Semiconductor 的 LED 驅動 IC，唯一發明人同名 "Tung-Ming Yu"，判定為同名誤入——若確為本人請告知，會加回 ITRI/Somnics 之外的第三組）。
- Somnics 頁只含公告號、名稱、日期、專利權人、發明人角色；不含任何內部管理欄位、未公開案件或技術描述。
