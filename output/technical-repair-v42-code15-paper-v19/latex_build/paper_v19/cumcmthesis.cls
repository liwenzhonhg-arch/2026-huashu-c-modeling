% cumcmthesis.cls - 简化版国赛论文模板类
% 基于 CUMCMThesis 项目精简，仅保留核心功能
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{cumcmthesis}[2024/01/01 CUMCM Thesis Template]

\newif\if@bindprint \@bindprintfalse
\newif\if@withoutpreface \@withoutprefacefalse
\newif\if@bwprint \@bwprintfalse

\DeclareOption{bindprint}{\@bindprinttrue}
\DeclareOption{withoutpreface}{\@withoutprefacetrue}
\DeclareOption{bwprint}{\@bwprinttrue}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax

\LoadClass[a4paper,12pt]{article}

\RequirePackage[UTF8,heading=true]{ctex}
\RequirePackage{geometry}
\RequirePackage{fancyhdr}
\RequirePackage{amsmath,amssymb,amsfonts}
\RequirePackage{graphicx}
\RequirePackage{booktabs}
\RequirePackage{float}
\RequirePackage{hyperref}
\RequirePackage{xcolor}

\geometry{
  top=30mm, bottom=25mm,
  left=30mm, right=30mm,
  headheight=14pt
}

\pagestyle{fancy}
\fancyhf{}
\fancyhead[C]{\small\leftmark}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}

% 标题格式
\ctexset{
  section/format = \Large\bfseries\centering,
  subsection/format = \large\bfseries,
  subsubsection/format = \normalsize\bfseries
}

% 摘要环境
\renewenvironment{abstract}{%
  \section*{摘\quad 要}
  \addcontentsline{toc}{section}{摘要}
}{%
  \par
}

% 关键词命令
\newcommand{\keywords}[1]{%
  \par\vspace{6pt}\noindent
  \textbf{关键词：}#1
}

\endinput
