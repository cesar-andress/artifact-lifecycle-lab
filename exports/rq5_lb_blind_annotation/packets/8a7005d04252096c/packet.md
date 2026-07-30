# Annotation packet `8a7005d04252096c`

Protocol: `RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md@e41902c`
Packet spec: `rq5_v1_blind_packet_spec_v2`

Judge only with the materials below. Do not seek external repositories or experimental results.

## Annotator question

Is Referenced artifact R1 materially necessary for completing THIS software engineering task in THIS repository snapshot?

## Anonymous snapshot

- Snapshot ID: `b30df23f49f5a1d2`
- Reference type: `directory`
- Artifact alias: **Referenced artifact R1**

## Task brief

Engineering task (derived only from the pinned instruction text and snapshot signals):

Document title: [[INSTRUCTION]]. Purpose Section: - This repository contains several related apps: a WinUI 3 client, an ASP.NET Core sync server, NUnit test projects, and a VitePress docs site. - Use this file as the fast path for build/test/style guidance before making changes. - When repo-specific instruction files conflict with generic habits, prefer the repo-specific instruction files. Instruction overview: ## Purpose - This repository contains several related apps: a WinUI 3 client, an ASP.NET Core sync server, NUnit test projects, and a VitePress docs site. - Use this file as the fast path for build/test/style guidance before making changes. - When repo-specific instruction files conflict with generic habits, prefer the repo-specific instruction files.

While performing this work, the instruction cites Referenced artifact R1. Your annotation question is whether that cited artifact is materially necessary for completing this task in the provided snapshot.

No automated verification command was identified from the pinned repository manifests. Judge necessity from the stated engineering task and the supplied snapshot materials only.

## Artifact role

Referenced artifact R1 is a repository artifact cited by the project instruction text (reference kind: directory). Its literal path string is withheld and shown as [[REF]] so treatment assignment cannot be inferred from path identity. Use the citation excerpts, task brief, and snapshot context below to judge relevance and necessity.

## Path policy

Path identity for the cited artifact and for contrast-only manipulated paths is replaced by [[REF]] using semantic whole-path tokenization (not substring replacement). Other snapshot paths may appear when they do not reveal treatment assignment. Do not infer experimental treatment from path placeholders.

## Instruction citation excerpts

### Excerpt 1

```
## Read These First
- Copilot rule found: `.github/copilot-instructions.md`.
- Its instruction is mandatory: before doing anything else, read `.kilocode/rules/project-main.md`.
- If you work on the client, also read `.kilocode/rules/project-info-galgamemanager.md`.
- If client work changes UI/XAML/custom controls, also read `.kilocode/rules/project-info-controls.md`.
- If you work on the server, also read `.kilocode/rules/project-info-galgamemanager-server.md`.
- Additional agent docs exist under `.github/.clinerules/`; they are not Cursor rules, but they contain useful repo knowledge.
- `.github/.clinerules/main.md` asks agents to update the `project-info` knowledge files with general reusable knowledge after finishing a task.
- No `[[REF]]` directory or `.cursorrules` file was found at repo root.

## Repository Map
- `GalgameManager/`: main WinUI 3 desktop client.
- `GalgameManager.Core/`: shared/core .NET library.
- `GalgameManager.Server/`: ASP.NET Core Web API sync server.
- `GalgameManager.Test/`: client-side NUnit tests.
- `GalgameManager.Server.Test/`: server-side NUnit tests.
- `PotatoVN.Doc/`: docs site built with VitePress.
```

## Repository tree excerpt (pinned snapshot)

```
".github/ISSUE_TEMPLATE/\346\226\260\345\212\237\350\203\275\345\273\272\350\256\256.md"
".github/ISSUE_TEMPLATE/\351\234\200\350\246\201\345\270\256\345\212\251.md"
.clinerules
.dockerignore
.editorconfig
.github/.clinerules/main.md
.github/.clinerules/project-info-galgamemanager-server.md
.github/.clinerules/project-info-galgamemanager.md
.github/.clinerules/project-info.md
.github/ISSUE_TEMPLATE/bug_report.md
.github/copilot-instructions.md
.github/workflows/build-signed-package.yml
.github/workflows/build.yml
.github/workflows/crowdin-fetch.yml
.github/workflows/crowdin-push.yml
.github/workflows/server-build-push.yml
.github/workflows/update-db.yml
.gitignore
.gitmodules
.kilocode/rules/project-info-controls.md
.kilocode/rules/project-info-galgamemanager-server.md
.kilocode/rules/project-info-galgamemanager.md
.kilocode/rules/project-main.md
.vsconfig
[[REF]]
Directory.Build.props
GalgameManager.sln
GalgameManager.sln.DotSettings
LICENSE
NuGet.Config
PotatoVN.Doc
PrivacyPolicy.md
README.md
crowdin.yml
```

## Neighbouring paths

_None listed in the minimal context window._

## Nearby documentation paths

```
[[REF]]
GalgameManager.Core/README.md
GalgameManager.Server/README.md
GalgameManager/README.md
README.md
docs/README_EN.md
```

## Nearby configuration paths

```
.github/workflows/build-signed-package.yml
.github/workflows/build.yml
.github/workflows/crowdin-fetch.yml
.github/workflows/crowdin-push.yml
.github/workflows/server-build-push.yml
.github/workflows/update-db.yml
FAQ/zh-CN.json
GalgameManager.Server/Dockerfile
GalgameManager.Server/Properties/launchSettings.json
GalgameManager.Server/appsettings.Development.json
```

## Pinned snapshot file excerpts

### snapshot_file_1

```
# [[INSTRUCTION]]

## Purpose
- This repository contains several related apps: a WinUI 3 client, an ASP.NET Core sync server, NUnit test projects, and a VitePress docs site.
- Use this file as the fast path for build/test/style guidance before making changes.
- When repo-specific instruction files conflict with generic habits, prefer the repo-specific instruction files.

## Read These First
- Copilot rule found: `.github/copilot-instructions.md`.
- Its instruction is mandatory: before doing anything else, read `.kilocode/rules/project-main.md`.
- If you work on the client, also read `.kilocode/rules/project-info-galgamemanager.md`.
- If client work changes UI/XAML/custom controls, also read `.kilocode/rules/project-info-controls.md`.
- If you work on the server, also read `.kilocode/rules/project-info-galgamemanager-server.md`.
- Additional agent docs exist under `.github/.clinerules/`; they are not Cursor rules, but they contain useful repo knowledge.
- `.github/.clinerules/main.md` asks agents to update the `project-info` knowledge files with general reusable knowledge after finishing a task.
- No `[[REF]]` directory or `.cursorrules` file was found at repo root.

## Repository Map
- `GalgameManager/`: main WinUI 3 desktop client.
- `GalgameManager.Core/`: shared/core .NET library.
- `GalgameManager.Server/`: ASP.NET Core Web API sync server.
- `GalgameManager.Test/`: client-side NUnit tests.
- `GalgameManager.Server.Test/`: server-side NUnit tests.
- `PotatoVN.Doc/`: docs site built with VitePress.
- `AuthServer/`: separate Flask-based auth component (Deperated, move into GalgameManager.Server).
- `GalgameManager.Tool/`: separate C++ utility project.
- `Directory.Build.props`: test platform defaults and Windows App SDK test overrides.
- `.editorconfig`: main formatting and naming rules.

## Environment Notes
- The client is Windows-specific and uses WinUI 3 plus Windows App SDK.
- Client packaging/build automation is MSBuild-based, not a simple cross-platform `d
```

### snapshot_file_2

```
﻿*Recommended Markdown Viewer: [Markdown Editor](https://marketplace.visualstudio.com/items?itemName=MadsKristensen.MarkdownEditor2)*

## Getting Started

The Core project contains code that can be [reused across multiple application projects](https://docs.microsoft.com/dotnet/standard/net-standard#net-5-and-net-standard).

```

### snapshot_file_3

```
# PotatoVN 同步服务器

## 简介
PotatoVN 同步服务器是一个用于帮助PotatoVN跨电脑同步/备份数据的服务器，它提供了一个RESTful API用于客户端与服务器之间的通信。

它能同步什么：[请参考potatovn wiki](https://potatovn.net/usage/advance/data-exchange.html)

## 部署
### 推荐部署方式：Docker (Compose)
1. 在服务器任意位置创建一个文件夹，它将用来存放docker-compose.yml文件及数据库数据。**以下操作均在此文件夹内进行**。
2. 下载docker-compose.yml文件：
'''shell
curl -O https://raw.githubusercontent.com/GoldenPotato137/PotatoVN/refs/heads/dev/GalgameManager.Server/docker-compose.yml
'''
> 国内服务器在访问github时可能会遇到网络问题，可以使用代理解决这个问题，或者直接下载docker-compose.yml文件到本地，然后上传到服务器。

3. 修改docker-compose.yml里必填内容，该文件内包含详细注释，按照注释填写即可。
'''shell
nano docker-compose.yml
'''

4. 新建一个`data`文件夹，并修改其权限，其用于存放数据库数据。
'''shell
mkdir data
sudo chown -R 1001:1001 ./data
'''
5. 测试性启动服务
'''shell
sudo docker-compose up
'''
检查是否正常启动，尝试用potatovn客户端链接服务器。如果你没有修改docker-compose.yml文件中的端口，
那么potatovn中应该输入的服务器地址为`http://你的服务器地址:8080` （如： http://192.168.114.114:8080）。

6. 如果一切正常，按`Ctrl+C`停止服务，然后使用以下命令正式启动服务：
'''shell
sudo docker-compose down
sudo docker-compose up -d
'''

7. （可选）使用https保护你的服务器，自行使用任何你喜欢的反向代理工具代理服务即可，如Nginx、Caddy等。

以下为一个简单的使用Caddy的配置文件示例：
'''caddy
your.domain.name {
    reverse_proxy localhost:8080
    encode zstd gzip
}
'''

### 二进制部署

> 请注意，二进制部署需要你自行安装并配置PostgreSQL数据库，以及设置环境变量。

该部分文档TODO

### 在测试环境中运行
初始化用户密钥:
'''shell
dotnet user-secrets init
'''
设置各类环境变量：
'''shell
dotnet user-secrets set "Key" "Value"
'''
应该设置的环境变量有（Key）：
* `ConnectionStrings:DefaultConnection` 数据库连接字符串，**数据库必须是PostgreSQL**
* `AppSettings:JwtKey` JWT秘钥，**至少64位长**
* `AppSettings:Minio:EndPoint` �
```

### snapshot_file_4

```
﻿name: Build And Sign Package

on:
  push:
    branches:
      - flight-released
      - released
  workflow_dispatch:

jobs:
  build:
    runs-on: windows-latest

    strategy:
      matrix:
        platform: ${{ github.ref_name == 'flight-released' && fromJSON('["x64"]') || fromJSON('["x86", "x64", "ARM64"]') }}

    env:
      BRANCH_NAME: ${{ github.ref_name }}

    steps:
      - uses: actions/checkout@v4

      - name: Install .NET Core
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: 8.0.x

      - name: Setup MSBuild.exe
        uses: microsoft/setup-msbuild@v2
        
      - name: Add WindowsAppSDKSelfContained
        shell: pwsh
        run: |
          $csprojPath = "GalgameManager/GalgameManager.csproj"
          # 读取 csproj 文件
          [xml]$xml = Get-Content $csprojPath
          # 筛选出包含 <TargetFramework> 的 PropertyGroup（主 PropertyGroup）
          $propertyGroup = $xml.Project.PropertyGroup | Where-Object { $_.TargetFramework }
          if (!$propertyGroup) {
            Write-Host "未找到包含 <TargetFramework> 的 PropertyGroup，改为使用第一个 PropertyGroup。"
            $propertyGroup = $xml.Project.PropertyGroup | Select-Object -First 1
            if (!$propertyGroup) {
              Write-Error "没有可用的 PropertyGroup。"
              exit 1
            }
          }
          # 如果当前没有 WindowsAppSDKSelfContained，则创建该节点并追加
          if (!$propertyGroup.WindowsAppSDKSelfContained) {
            $newElement = $xml.CreateElement("WindowsAppSDKSelfContained")
            $newElement.InnerText = "true"
            $propertyGroup.AppendChild($newElement) | Out-Null
          }
          # 保存
          $xml.Save($csprojPath)

      - name: Set PUBLISHER
        run: |
          $manifestPath = "GalgameManager\Package.appxmanifest"
          if (!(Test-Path $manifestPath)) {
            Write-Error "无法找到 AppxManifest.xml 文件，路径为 $manifestPath"
            exit 1
          }
          [xml]$xml = Get-Content $manifestPath
          $xml.Packag
```

### snapshot_file_5

```
name: build

on:
  workflow_dispatch:
  push:
    branches:
      - dev
    paths:
      - 'GalgameManager/**'
      - 'GalgameManager.Core/**'
      - 'GalgameManager.Server/**'
      - 'GalgameManager.Test/**'
  pull_request:
    paths:
      - 'GalgameManager/**'
      - 'GalgameManager.Core/**'
      - 'GalgameManager.Server/**'
      - 'GalgameManager.Test/**'

jobs:
  build:
    runs-on: windows-latest

    strategy:
      matrix:
        platform: ["x86", "x64", "ARM64"]
    
    steps:
    - uses: actions/checkout@v4

    - name: Install .NET Core
      uses: actions/setup-dotnet@v4
      with:
        dotnet-version: 8.0.x

    - name: Setup MSBuild.exe
      uses: microsoft/setup-msbuild@v2

    - name: Update version
      shell: pwsh
      run: |
        $manifestPath = "GalgameManager/Package.appxmanifest"
        [xml]$manifest = Get-Content $manifestPath
        $version = $manifest.Package.Identity.Version
        $versionParts = $version.Split('.')
        $versionParts[3] = [string]([int]$versionParts[3] + 1)
        $versionParts[3] = $env:GITHUB_RUN_NUMBER
        $newVersion = [string]::Join('.', $versionParts)
        $manifest.Package.Identity.Version = $newVersion
        $manifest.Save($manifestPath)
        echo "Updated version to $newVersion"

    - name: Update app icon
      shell: pwsh
      run: |
        xcopy "GalgameManager\Assets\Pictures\icon-dev\*" "GalgameManager\Assets\" /s /e /y
        echo "Updated app icon"

    - name: Create the app package
      run: msbuild GalgameManager\GalgameManager.csproj /restore "/p:Platform=${{ matrix.platform }};Configuration=Release;UapAppxPackageBuildMode=SideloadOnly;AppxPackageDir=..\publish\;GenerateAppxPackageOnBuild=true;AppxPackageSigningEnabled=true;PackageCertificateKeyFile=GalgameManager_TemporaryKey.pfx"

    - name: Move package
      shell: pwsh
      run: |
        # 将 msix 和 cer 移动到 publish 根目录
        $subFolder = Get-ChildItem -Path publish -Directory | Select-Object -First 1
```

### snapshot_file_6

```
﻿name: Crowdin Fetch Action

on:
  workflow_dispatch:
    
permissions: write-all

jobs:
  crowdin:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Synchronize with Crowdin
        uses: crowdin/github-action@v1
        with:
          upload_sources: false
          upload_translations: false
          download_translations: true
          localization_branch_name: l10n_crowdin_translations

          create_pull_request: true
          pull_request_title: 'New Crowdin translations'
          pull_request_body: 'New Crowdin pull request with translations'
          pull_request_base_branch_name: 'dev'
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          CROWDIN_PROJECT_ID: 581621
          CROWDIN_PERSONAL_TOKEN: ${{ secrets.CROWDIN_PERSONAL_TOKEN }}

```
