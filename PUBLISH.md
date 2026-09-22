# 发布手册 · Git 仓库初始化与推送

本文档沉淀了 `orbit-salvage` 从 0 到 GitHub 的完整命令序列，以及常见冲突、大文件、密钥问题的处置办法。
所有命令均可在项目根目录直接复制执行。

> 技术栈：原生 HTML5 / Canvas / JS + Python 3 标准库（零构建、零依赖）

---

## 一、从零到远端：完整命令序列

```bash
# 0) 进入项目根目录
cd /path/to/orbit-salvage

# 1) 初始化仓库，main 作为主分支
git init -b main

# 2) 确认忽略规则生效（依赖 / 构建产物 / 日志 / 密钥）
git status --short          # 不应出现 node_modules/、__pycache__/、.env 等
git check-ignore -v .env node_modules dist  # 验证忽略是否命中

# 3) 首次提交
git add -A
git commit -m "feat: 星轨回收者 Orbit Salvage 首版"

# 4) 打版本标签
git tag -a v1.0.0 -m "v1.0.0 首个可玩版本"

# 5) 关联远端（SSH，走 443 端口，本机 HTTPS 直连 GitHub 不通）
git remote add origin git@github.com:AyaseEli-Bing/orbit-salvage.git

# 6) 推送所有分支与标签
git push -u origin main
git push origin --tags

# —— 若要「所有分支 + 所有标签」一次到位 ——
git push -u origin --all && git push origin --tags
```

**后续日常提交**

```bash
git add -A
git commit -m "fix: 描述改动"
git push origin main
```

---

## 二、远端仓库已存在（非空仓库 / 自带 README）

GitHub 新建仓库时若勾选了 README / LICENSE / .gitignore，**远端已有一次提交**，本地会与之无共同祖先，直接 push 会被拒。

**方案 A（推荐）：先把远端历史拉下来再变基**

```bash
git remote add origin git@github.com:AyaseEli-Bing/orbit-salvage.git
git pull --rebase origin main --allow-unrelated-histories
# 若 README.md 冲突：手动保留需要的内容 -> git add README.md -> git rebase --continue
git push -u origin main
```

**方案 B：远端改成真正的空仓库**
在 GitHub 仓库 Settings → Danger Zone → 删除重建，或删掉远端自带的 README 提交后再 push。

**方案 C：换个仓库名**
`git remote set-url origin git@github.com:AyaseEli-Bing/<新仓库名>.git`

> 若远端已有内容且本地是全新项目、确定要完全覆盖：`git push -u --force-with-lease origin main`（比 `--force` 安全，会在远端有他人新提交时拒绝）。

---

## 三、remote 冲突与常见报错

| 症状 | 原因 | 处置 |
|------|------|------|
| `error: remote origin already exists` | origin 已配置 | `git remote set-url origin <新地址>`（改地址）或 `git remote remove origin` 后重建 |
| `Repository not found` | 远端仓库不存在 / 无权限 / SSH key 未注册 | 确认仓库已创建且 owner 正确；`ssh -T git@github.com` 验证身份 |
| `Permission denied (publickey)` | SSH 密钥未加到 GitHub 或端口被封 | 确认 `~/.ssh/id_ed25519.pub` 已添加到账号；22 端口不通时在 `~/.ssh/config` 里把 `HostName` 改为 `ssh.github.com`、`Port 443` |
| `failed to push some refs (non-fast-forward)` | 远端有新提交 | `git pull --rebase origin main` 后重新 push |
| `src refspec main does not match any` | 本地还没提交 | 先 `git add -A && git commit -m "..."` |
| `gh: The token in keyring is invalid` | gh CLI 凭据过期 | `gh auth login -w` 重新登录（需浏览器 OAuth）；本机 HTTPS 不通时改用 SSH 推送即可 |

**查看与修正**

```bash
git remote -v                                  # 查看当前远端
git remote set-url origin git@github.com:AyaseEli-Bing/orbit-salvage.git
git config --get branch.main.remote            # 确认上游跟踪
git branch -vv                                 # 查看分支跟踪关系
```

---

## 四、大文件处理

GitHub 单文件上限 **100 MB**（超过会被拒绝），仓库建议控制在 **1 GB** 以内。

**推送前自查**

```bash
# 列出工作区最大的文件
find . -path ./.git -prune -o -type f -size +10M -print

# 列出 git 历史中体积最大的对象
git rev-list --objects --all \
  | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' \
  | sort -k3 -n -r | head -20
```

**已经误提交了大文件 → 清理历史**

```bash
# 推荐：git filter-repo（需 pip install git-filter-repo）
git filter-repo --strip-blobs-bigger-than 100M

# 或按路径移除某个文件
git filter-repo --path <大文件路径> --invert-paths

# 清理后强制推送（会改写历史，务必先通知协作者）
git push origin --force --all
```

**确实需要版本化管理大文件 → Git LFS**

```bash
git lfs install
git lfs track "*.psd" "*.mp4" "*.zip"     # 会写入 .gitattributes
git add .gitattributes
git commit -m "chore: 接入 Git LFS"
git push origin main
```

> 本项目当前总计约 56 KB（index.html 44 KB），远低于阈值，无需 LFS。

---

## 五、密钥与敏感信息

`.gitignore` 已排除：`.env*`、`.npmrc`、`.pypirc`、`.netrc`、`*.pem` / `*.key` / `*.p12`、SSH 私钥、`credentials*`、`secrets*`、`service-account*.json` 等。

**提交前自检**

```bash
git diff --cached | grep -nEi "AKIA[0-9A-Z]{16}|BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|(password|secret|token|api[_-]?key)\s*[:=]"
```

**万一已经提交：先吊销，再清历史**

1. 立刻到对应平台吊销泄露的 token / key（这一步优先于任何 git 操作）；
2. 用 `git filter-repo --path .env --invert-paths` 清除历史中的文件；
3. `git push --force --all` 并通知所有协作者重新 clone。

---

## 六、本机环境备注

- **SSH 可用**：`ssh -T git@github.com` 返回 `Hi AyaseEli-Bing!`，账号为 `AyaseEli-Bing`（带连字符）。
- **HTTPS 不可用**：`curl https://api.github.com` / `https://github.com` 均返回 `000`（连接失败），因此 `gh` CLI 即便重新登录，多数依赖 API 的命令仍会失败 —— 建仓与推送统一走 SSH 更稳。
- 若 `~/.ssh/config` 把 `github.com` 重定向到了 `ssh.github.com:443`，则 HTTPS fetch 会被一起改写，属预期行为。
