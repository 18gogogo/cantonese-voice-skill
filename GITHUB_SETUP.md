# GitHub 倉庫設置指南

## 1. 創建 GitHub 倉庫

1. 登錄 GitHub: https://github.com
2. 點擊右上角 "+" → "New repository"
3. 設置倉庫：
   - Repository name: `cantonese-voice-skill`
   - Description: "Cantonese Voice Skill for OpenClaw, supporting Qwen32B-Q4, Llama, Claude, etc."
   - Public/Private: 根據需要選擇
   - 不要勾選 "Initialize with README"
4. 點擊 "Create repository"

## 2. 推送到 GitHub

### 方法 1: 使用 SSH（推薦）

```bash
cd /home/ubuntu/.openclaw/workspace/skills/cantonese-voice

# 添加遠程倉庫（替換為你的 GitHub 用戶名）
git remote add origin git@github.com:YOUR_USERNAME/cantonese-voice-skill.git

# 推送
git push -u origin master
```

### 方法 2: 使用 HTTPS

```bash
cd /home/ubuntu/.openclaw/workspace/skills/cantonese-voice

# 添加遠程倉庫（替換為你的 GitHub 用戶名）
git remote add origin https://github.com/YOUR_USERNAME/cantonese-voice-skill.git

# 推送
git push -u origin master
```

## 3. 後續使用

### 提交更新

```bash
git add .
git commit -m "Update message"
git push
```

### 查看狀態

```bash
git status
git log --oneline
```

## 4. 更新 SKILL.md 和 README.md

如果需要更新文檔：

```bash
# 編輯文件
nano SKILL.md

# 提交
git add SKILL.md
git commit -m "Update SKILL.md"
git push
```

## 5. 克隆到其他環境

```bash
git clone https://github.com/YOUR_USERNAME/cantonese-voice-skill.git
cd cantonese-voice-skill
```

---

**注意**: 記得把 `YOUR_USERNAME` 替換成你的 GitHub 用戶名！
