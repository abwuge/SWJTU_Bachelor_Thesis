<div align="center">
  <h1>西南交通大学本科毕业论文LaTeX模板</h1>
  
  [![LICENSE](https://badgen.net/static/LICENSE/非商业许可)](LICENSE)
</div>

---

> [!TIP]
>
> 0. 截至 2026 年毕业季，该仓库仍在维护，如有任何问题请及时提交[Issue](../../issues/new)或[Pull Request](../../pulls)。
> 1. 截至 2025 年毕业季，教务网只支持 doc/docx 格式论文。但仅需将编译后的 pdf 直接转为 word 提交至教务网即可，即使直接转换后的 word 格式杂乱。
> 2. 若需详细论文撰写示例，可通过[许可证](LICENSE)中的联系方式向仓库所有者获取其本科毕业论文仓库权限。

## 简介

本项目为西南交通大学本科毕业设计（论文）LaTeX 模板，依据《西南交通大学本科毕业设计（论文）撰写规范》（2022 年修订稿）进行设计。

点击[此处](https://abwuge.github.io/SWJTU_Bachelor_Thesis/SWJTU_Bachelor_Thesis.pdf)预览该模板。

## 使用说明

### 创建项目

1. 克隆或从[Release](../../releases/latest)下载本项目到本地：
    ```shell
    git clone https://github.com/abwuge/SWJTU_Bachelor_Thesis.git
    ```
2. 打开项目文件夹。
3. 将`SWJTU_Bachelor_Thesis.tex`中的示例内容修改为个人论文内容。
4. 按照论文结构，在`chapters/`、`appendix/`等文件夹中编辑各章节内容。
5. 编译主文件，生成 PDF 论文。请使用 XeLaTeX 进行编译：

    Windows PowerShell:

    ```powershell
    "build/appendix", "build/chapters" | % { md -Force $_ }
    xelatex -synctex=1 -interaction=nonstopmode -file-line-error -output-directory=build SWJTU_Bachelor_Thesis.tex
    biber --output-directory=build SWJTU_Bachelor_Thesis
    xelatex -synctex=1 -interaction=nonstopmode -file-line-error -output-directory=build SWJTU_Bachelor_Thesis.tex
    xelatex -synctex=1 -interaction=nonstopmode -file-line-error -output-directory=build SWJTU_Bachelor_Thesis.tex
    ```

    Shell:

    ```shell
    mkdir -p build/appendix build/chapters
    xelatex -synctex=1 -interaction=nonstopmode -file-line-error -output-directory=build SWJTU_Bachelor_Thesis.tex
    biber --output-directory=build SWJTU_Bachelor_Thesis
    xelatex -synctex=1 -interaction=nonstopmode -file-line-error -output-directory=build SWJTU_Bachelor_Thesis.tex
    xelatex -synctex=1 -interaction=nonstopmode -file-line-error -output-directory=build SWJTU_Bachelor_Thesis.tex
    ```

    > 编译链：xelatex -> biber -> xelatex\*2

6. 参考文献请在`bibliography/references.bib`中维护。

你也可以将本模板上传到[Overleaf](https://cn.overleaf.com/)平台进行在线编写：

1. 从[Release](../../releases/latest)中下载最新版本的源代码压缩包。
2. 在 Overleaf 创建新项目，上传项目压缩包。
3. 打开项目后，点击左上角菜单，并将编译器从 pdfLaTeX 改为 XeLaTeX。
4. 点击右上角重新编译，即可正常编译项目。

或者点击[此处](https://abwuge.github.io/SWJTU_Bachelor_Thesis)直接在 Overleaf 中创建该项目。

<details>
<summary><del>但是论文后期貌似会编译超时</del></summary>
也可能是我的论文比较复杂，不过如果真想用Overleaf可以氪金啦
</details>

### 宏包键值对参数介绍

-   `[ ]` `major`：所在专业，请使用教务处的标准专业名称。

    > 不同专业的论文要求可能不同，若不手动设置专业名称，将使用西南交通大学提供的模板作为默认模板。
    > 若无您需要的专业，请提交[Issue](../../issues/new)或[Pull Request](../../pulls)。

    > 当前已实现专业（按首字笔画数量排序）：
    >
    > -   计算机与人工智能学院
    >     -   人工智能
    >     -   计算机科学与技术
    >     -   软件工程
    > -   物理科学与技术学院
    >     -   应用物理学

### 模板自定义命令介绍

#### 无参数命令

-   `\songti`：将中文切换到模板内置字体——宋体。
-   `\heiti`：将中文切换到模板内置字体——黑体。
-   `\ensongti`：将英文切换到模板内置字体——宋体。
-   `\enheiti`：将英文切换到模板内置字体——黑体。
-   `\boxsurd`：在当前位置生成已选中的复选框。
-   `\swjtuTableOfContents`：生成目录页。

#### 普通参数命令

-   `\swjtuIntroduction{章节名}`：生成绪论章节（会重置页码并开始阿拉伯数字编号）。
-   `\swjtuChapter{章节名}`：生成普通章节。
-   `\swjtuConclusion{章节名}`：生成结论章节（无编号章节，但会加入目录）。
-   `\swjtuAcknowledgments{章节名}`：生成致谢章节（与结论章节相同格式）。
-   `\swjtuBibliography{章节名}`：生成参考文献章节（无编号章节，但会加入目录）。
-   `\swjtuAppendix{章节名}`：生成附录章节（使用"附录 1"、"附录 2"等编号）。
-   `\swjtuExplanation{符号, 解释; ...}`：生成公式的符号注释。
    ```latex
    % 使用示例
    % 若符号或解释本身含有分隔符，用`{}`包围即可，`{}`本身也可嵌套
    \swjtuExplanation{
      符号1, 解释1;
      {含有","的符号2}, {含有";"或"{}"的解释2};
    }
    ```

#### 代码块相关命令

-   `\Input`：在算法环境中生成"输入："标签。
-   `\Output`：在算法环境中生成"输出："标签。

#### 键值对参数命令

-   `\swjtuTitlePage`：生成扉页。
    -   `[ ]` `ctitle`：中文标题。
    -   `[ ]` `etitle`：英文标题。
    -   `[ ]` `grade`：年级。
    -   `[ ]` `id`：学号。
    -   `[ ]` `name`：姓名。
    -   `[ ]` `major`：专业。
    -   `[ ]` `advisor`：指导老师。
    -   `[ ]` `year`：年份。
    -   `[ ]` `month`：月份。
-   `\swjtuIntegrityDeclaration`：生成学术诚信声明页。
    -   `[ ]` `signature`：作者签名图片路径。
    -   `[ ]` `year`：年份。
    -   `[ ]` `month`：月份。
    -   `[ ]` `day`：日期。
-   `\swjtuCopyrightAuthorization`：生成版权使用授权书。
    -   `[0]` `confidentialityPeriod`：保密年限，小于等于 0 为不保密。
    -   `[ ]` `authorSignature`：作者签名图片路径。
    -   `[ ]` `advisorSignature`：指导教师签名图片路径。
    -   `[ ]` `authorYear`/`authorMonth`/`authorDay`：作者签署日期。
    -   `[ ]` `advisorYear`/`advisorMonth`/`advisorDay`：指导教师签署日期。
-   `\swjtuTask`：生成任务书。
    -   `[ ]` `class`：班级。
    -   `[ ]` `name`：姓名。
    -   `[ ]` `id`：学号。
    -   `[ ]` `issueYear`/`issueMonth`/`issueDay`：发题日期。
    -   `[ ]` `dueYear`/`dueMonth`/`dueDay`：完成日期。
    -   `[ ]` `title`：课题题目。
    -   `[ ]` `purpose`：目的意义。
    -   `[ ]` `tasks`：应完成的任务。
    -   `[ ]` `requirement`：毕业要求达成度。
    -   `[ ]` `weeks`：总周数。
    -   `[ ]` `partOne`/`partOneWeeks` ~ `partFive`/`partFiveWeeks`：各部分内容及周数。
    -   `[ ]` `partReview`/`partReviewWeeks`：评阅及答辩内容及周数。
    -   `[ ]` `remark`：备注。
    -   `[ ]` `advisorSignature`：指导教师签名图片路径。
    -   `[ ]` `advisorYear`/`advisorMonth`/`advisorDay`：指导教师签署日期。
    -   `[ ]` `approverSignature`：审批人签名图片路径（仅应用物理学专业使用）。
    -   `[ ]` `approverYear`/`approverMonth`/`approverDay`：审批人签署日期（仅应用物理学专业使用）。
-   `\swjtuAbstractCN`：生成中文摘要。
    -   `[ ]` `abstract`：中文摘要正文。
    -   `[ ]` `keywords`：中文关键词（请自行用分号分隔）。
-   `\swjtuAbstractEN`：生成英文摘要。
    -   `[ ]` `abstract`：英文摘要正文。
    -   `[ ]` `keywords`：英文关键词（请自行用分号分隔）。

**注 1**：键值对参数命令的参数均为可选参数。在参数名之前用`[]`表示其默认值。

> 例如：`[ ]`表示默认参数为空，`[0]`表示默认参数为 0。

**注 2**：由于本人能力有限，模板中部分自定义命名中修改了全局定义。因此若您未按照主文件示例的命令执行方式进行论文撰写，恐有非预期行为。

### 模板自定义环境说明

-   `allsongti`：中英文字体均设置为内置字体——宋体。
-   `allheiti`：中英文字体均设置为内置字体——黑体。
-   `swjtuCodeBlock`：代码框环境，支持语法高亮和行号显示。
-   `emptyPage`：创建一个完全空白的页面（无页眉页脚）。
-   `fancyPage`：创建一个带有页眉页脚的页面。
-   `explainSymbol`：用于公式符号解释的特殊列表环境（由`\swjtuExplanation`命令内部使用）。

### 模板预定义的表格列类型

-   `L`：左对齐的可变宽度列（用于`tabularx`环境）。
-   `C`：居中对齐的可变宽度列（用于`tabularx`环境）。
-   `R`：右对齐的可变宽度列（用于`tabularx`环境）。

## 目录结构说明

```powershell
.
│  LICENSE                   # 许可证
│  SWJTU_Bachelor_Thesis.tex # 主文件
│
├─appendix # 附录
│      appendix1.tex
│      appendix2.tex
│
├─bibliography # 参考文献
│      references.bib
│
├─chapters # 主体
│      acknowledgments.tex # 致谢
│      chapter1.tex        # 正常章节
│      conclusion.tex      # 结论
│      introduction.tex    # 绪论
│
├─fonts # 模板内置字体（取自Windows，商用请注意版权）
│      simhei.ttf  # 黑体
│      simsun.ttc  # 宋体
│      TIMES.TTF   # 新罗马正常
│      TIMESBD.TTF # 新罗马粗体
│      TIMESBI.TTF # 新罗马粗斜
│      TIMESI.TTF  # 新罗马斜体
│
├─signatures # 电子签名图片
│      advisor.png  # 指导教师签名
│      approver.png # 审批人签名（仅应用物理学专业使用）
│      author.png   # 作者签名
│
└─style # 格式文件
        swjtu.sty
```

## :+1: VS Code 配置说明

可以使用 [Visual Studio Code](https://code.visualstudio.com/) 进行论文编写，配合 [LaTeX Workshop](https://marketplace.visualstudio.com/items?itemName=James-Yu.latex-workshop) 插件可获得良好体验。你可以将如下 settings.json 配置文件放置于 `.vscode/settings.json`：

```json
{
    "latex-workshop.latex.outDir": "./build",
    "latex-workshop.latex.recipes": [
        {
            "name": "xelatex -> biber -> xelatex*2",
            "tools": ["xelatex", "biber", "xelatex", "xelatex"]
        }
    ],
    "latex-workshop.latex.tools": [
        {
            "name": "xelatex",
            "command": "xelatex",
            "args": [
                "-synctex=1",
                "-interaction=nonstopmode",
                "-file-line-error",
                "-output-directory=build",
                "%DOC%"
            ]
        },
        {
            "name": "biber",
            "command": "biber",
            "args": ["--output-directory=build", "%DOCFILE%"]
        }
    ],
    "latex-workshop.formatting.latexindent.args": [
        "-c",
        "%DIR%/build/",
        "%TMPFILE%",
        "-y=defaultIndent: '%INDENT%'"
    ]
}
```

Windows 下的[TeX Live](https://tug.org/texlive/) & [VS Code](https://code.visualstudio.com/)配置方法可参考[知乎文章](https://zhuanlan.zhihu.com/p/382472221)。

## 贡献

### 贡献指南

欢迎大家为本模板贡献代码、修正 bug 或完善文档！

-   如有建议或问题，请提交 Issue。
-   欢迎提交 Pull Request。
-   贡献前请确保遵循各自专业的最新论文撰写规范。

### 感谢所有贡献者！

[![贡献者](https://contrib.rocks/image?repo=abwuge/SWJTU_Bachelor_Thesis)](https://github.com/abwuge/SWJTU_Bachelor_Thesis/graphs/contributors)

### Star

> [!TIP]
> 若对您有帮助，请给这个项目点上 Star!

<a href="https://www.star-history.com/#abwuge/SWJTU_Bachelor_Thesis&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=abwuge/SWJTU_Bachelor_Thesis&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=abwuge/SWJTU_Bachelor_Thesis&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=abwuge/SWJTU_Bachelor_Thesis&type=Date" />
 </picture>
</a>
