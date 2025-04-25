# 西南交通大学本科毕业论文LaTeX模板

## 开发进度
- 完成扉页
- 完成扉页后空白页
- 完成学术诚信声明
- 完成版权使用授权
- 完成任务书
- 完成摘要

## 简介
本项目为西南交通大学本科毕业设计（论文）LaTeX模板，依据《西南交通大学本科毕业设计（论文）撰写规范》（2022年修订稿）进行设计。

## 使用说明
1. 克隆或下载本项目到本地：
   ```powershell
   git clone <仓库地址>
   ```
2. 使用支持LaTeX的编辑器（如TeX Live + VS Code、TeXworks等）打开`SWJTU_Bachelor_Thesis.tex`主文件。
3. 按照论文结构，在`chapters/`、`appendix/`等文件夹中编辑各章节内容。
4. 编译主文件，生成PDF论文。推荐使用XeLaTeX进行编译以支持中文：
   ```powershell
   xelatex SWJTU_Bachelor_Thesis.tex
   bibtex SWJTU_Bachelor_Thesis.aux
   xelatex SWJTU_Bachelor_Thesis.tex
   xelatex SWJTU_Bachelor_Thesis.tex
   ```
5. 参考文献请在`bibliography/references.bib`中维护。
6. 你也可以将本模板上传到Overleaf平台进行在线编写，只需在Overleaf的“菜单-编译器”中选择XeLaTeX即可，无需其他特殊设置。

## 目录结构说明
- `SWJTU_Bachelor_Thesis.tex`：主控文件。
- `chapters/`：各章节内容。
- `appendix/`：附录内容。
- `bibliography/`：参考文献数据库。
- `style/swjtu.sty`：模板样式文件。
- `fonts/`：所需字体文件。
- `build/`：编译生成的中间文件和PDF。

## VS Code 配置说明
可以使用 VS Code 进行论文编写，配合 LaTeX Workshop 插件可获得良好体验。你可以将如下 settings.json 配置文件放置于 `.vscode/settings.json`：

```json
{
    "latex-workshop.latex.outDir": "build",
    "latex-workshop.latex.recipes": [
        {
            "name": "xelatex",
            "tools": [
                "xelatex"
            ]
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

详细配置方法和 VS Code + LaTeX Workshop 的使用技巧可参考[知乎文章](https://zhuanlan.zhihu.com/p/382472221)。

## 贡献指南
欢迎大家为本模板贡献代码、修正bug或完善文档！
- 如有建议或问题，请提交Issue。
- 欢迎提交Pull Request。
- 贡献前请确保遵循《西南交通大学本科毕业设计（论文）撰写规范》（2022年修订稿）。

## 致谢
感谢所有为本模板做出贡献的同学和老师！

---
本模板仅供学习和学术用途，严禁任何商业用途。
