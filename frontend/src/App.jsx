import { useState, useRef, useEffect } from 'react'
import { Send, User, Bot, Loader2, Settings, MessageSquare, Database, FileText, UploadCloud, Trash2, RefreshCw, Activity, Save, Lock, ArrowLeft, KeyRound } from 'lucide-react'
import './App.css'

// ==========================================
// 0. 管理员登录组件 (新增)
// ==========================================
function AdminLogin({ onLogin, onCancel }) {
  const [password, setPassword] = useState('')
  const [error, setError] = useState(false)

  const handleLogin = () => {
    // 🔒 这里设置你的管理员密码
    if (password === 'admin888') {
      onLogin(true)
    } else {
      setError(true)
      setPassword('')
    }
  }

  return (
    <div className="login-overlay">
      <div className="login-card">
        <div className="login-icon">
          <Lock size={32} />
        </div>
        <h2 className="login-title">管理员验证</h2>
        <p className="login-subtitle">请出示您的通行证以进入控制台</p>

        <input
          type="password"
          className="login-input"
          placeholder="请输入密码"
          value={password}
          onChange={e => {setPassword(e.target.value); setError(false)}}
          onKeyDown={e => e.key === 'Enter' && handleLogin()}
          style={{borderColor: error ? '#fc8181' : ''}}
          autoFocus
        />

        <button className="login-btn" onClick={handleLogin}>
          解锁进入
        </button>

        <button className="login-back" onClick={onCancel}>
          <ArrowLeft size={14} style={{verticalAlign: 'middle', marginRight: '4px'}}/>
          返回聊天
        </button>
      </div>
    </div>
  )
}

// ==========================================
// 1. 管理后台组件 (Admin Panel)
// ==========================================
function AdminView() {
  const [config, setConfig] = useState({ model: '', temperature: 0.2 })
  const [files, setFiles] = useState([])
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)

  useEffect(() => {
    fetchConfig()
    fetchFiles()
    fetchLogs()
  }, [])

  const fetchConfig = async () => {
    try {
        const res = await fetch('http://127.0.0.1:8000/api/v1/admin/config')
        const data = await res.json()
        setConfig(data)
    } catch (e) { console.error("配置加载失败", e) }
  }

  const fetchFiles = async () => {
    try {
        const res = await fetch('http://127.0.0.1:8000/api/v1/admin/files')
        const data = await res.json()
        setFiles(data.files || [])
    } catch (e) { console.error("文件列表加载失败", e) }
  }

  const fetchLogs = async () => {
    try {
        const res = await fetch('http://127.0.0.1:8000/api/v1/admin/logs?size=20')
        const data = await res.json()
        setLogs(data.logs || [])
    } catch (e) { console.error("日志加载失败", e) }
  }

  const handleSaveConfig = async () => {
    setLoading(true)
    try {
      await fetch('http://127.0.0.1:8000/api/v1/admin/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      })
      alert('配置已更新！')
    } catch(e) {
      alert('更新失败: ' + e)
    }
    setLoading(false)
  }

  const handleUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    setUploading(true)
    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/admin/upload', {
        method: 'POST',
        body: formData
      })
      if (res.ok) {
        alert('上传成功！请点击“重建索引”以生效。')
        fetchFiles()
      } else {
        alert('上传失败')
      }
    } catch(e) {
      alert('错误: ' + e)
    }
    setUploading(false)
  }

  const handleDeleteFile = async (filename) => {
    if (!confirm(`确定要删除 ${filename} 吗？`)) return
    await fetch(`http://127.0.0.1:8000/api/v1/admin/files/${filename}`, { method: 'DELETE' })
    fetchFiles()
  }

  const handleRebuild = async () => {
    setLoading(true)
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/admin/rebuild', { method: 'POST' })
      const data = await res.json()
      alert(data.message)
    } catch(e) {
      alert('重建失败: ' + e)
    }
    setLoading(false)
  }

  return (
    <div className="admin-container">
      {/* 1. 系统配置卡片 */}
      <div className="admin-card">
        <div className="card-title"><Settings size={20} /> 系统大脑配置</div>
        <div className="form-group">
          <label>AI 模型 (Model)</label>
          <select
            className="form-control"
            value={config.model || ''}
            onChange={e => setConfig({...config, model: e.target.value})}
          >
            <option value="gpt-3.5-turbo">GPT-3.5 Turbo (快速/便宜)</option>
            <option value="gpt-4.1-mini">GPT-4 (聪明/昂贵)</option>
            <option value="gemini-3-pro-preview">Gemini3(最新全能)</option>
            <option value="deepseek-chat">DeepSeek V3 (高性价比)</option>
          </select>
        </div>
        <div className="form-group">
          <label>回答温度 (Temperature): {config.temperature}</label>
          <input
            type="range" className="form-control"
            min="0" max="2" step="0.1"
            value={config.temperature || 0.2}
            onChange={e => setConfig({...config, temperature: parseFloat(e.target.value)})}
          />
          <small style={{color: '#666'}}>数值越低回答越严谨(0.1)，数值越高回答越发散(0.8)。</small>
        </div>
        <button className="btn-primary" onClick={handleSaveConfig} disabled={loading}>
          <Save size={16} /> 保存配置
        </button>
      </div>

      {/* 2. 知识库管理卡片 */}
      <div className="admin-card">
        <div className="card-title"><Database size={20} /> 知识库文件管理</div>
        <div style={{display: 'flex', gap: '10px', marginBottom: '15px'}}>
          <label className="btn-primary" style={{cursor: 'pointer'}}>
            <UploadCloud size={16} />
            {uploading ? '上传中...' : '上传新文档 (.txt / .pdf)'}
            <input type="file" accept=".txt,.pdf" hidden onChange={handleUpload} disabled={uploading}/>
          </label>
          <button className="btn-primary" style={{background: '#38a169'}} onClick={handleRebuild} disabled={loading}>
            <RefreshCw size={16} /> {loading ? '重建中...' : '重建索引 (让AI学习)'}
          </button>
        </div>

        <div className="file-list">
          {files.map(file => (
            <div key={file} className="file-item">
              <span className="file-name"><FileText size={16}/> {file}</span>
              <button className="btn-danger" onClick={() => handleDeleteFile(file)}>
                <Trash2 size={14}/> 删除
              </button>
            </div>
          ))}
          {files.length === 0 && <div style={{color:'#aaa', textAlign:'center'}}>暂无文件，请上传</div>}
        </div>
      </div>

      {/* 3. 日志审计卡片 */}
      <div className="admin-card">
        <div className="card-title"><Activity size={20} /> 最近对话日志 (Top 20)</div>
        <div className="log-table-wrapper">
          <table className="log-table">
            <thead>
              <tr>
                <th>时间</th>
                <th>用户问题</th>
                <th>AI 回答</th>
              </tr>
            </thead>
            <tbody>
              {logs.map(log => (
                <tr key={log.id}>
                  <td className="log-time">{new Date(log.created_at).toLocaleString()}</td>
                  <td style={{maxWidth: '200px'}}>{log.user_question}</td>
                  <td style={{maxWidth: '300px', color: '#666'}}>{log.ai_answer.substring(0, 50)}...</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

// ==========================================
// 2. 聊天组件 (Chat View)
// ==========================================
function ChatView() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState([
    { role: 'assistant', content: '您好呀！我是敏宝守护者。宝宝最近有什么过敏问题吗？💕' }
  ])
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }
  useEffect(scrollToBottom, [messages])

  const handleSend = async () => {
    if (!input.trim() || isLoading) return
    const userQuestion = input
    setInput('')
    setIsLoading(true)
    setMessages(prev => [...prev, { role: 'user', content: userQuestion }])

    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: userQuestion }),
      })
      const data = await response.json()
      if (response.ok) {
        setMessages(prev => [...prev, { role: 'assistant', content: data.answer }])
      } else {
        setMessages(prev => [...prev, { role: 'assistant', content: '⚠️ 出错了：无法连接到大脑。' }])
      }
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: '🚫 网络错误，请检查后端是否启动。' }])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="chat-container" style={{flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden'}}>
      <div className="chat-box">
        {messages.map((msg, index) => (
          <div key={index} className={`message-row ${msg.role === 'user' ? 'user-row' : 'bot-row'}`}>
            <div className={`avatar ${msg.role}`}>
              {msg.role === 'user' ? <User size={20} /> : <Bot size={20} />}
            </div>
            <div className={`bubble ${msg.role}`}>
              {msg.content}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="message-row bot-row">
            <div className="avatar assistant"><Bot size={20} /></div>
            <div className="bubble assistant loading-bubble"><Loader2 className="spinner" size={16} /> 正在思考...</div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="input-area">
        <div className="input-wrapper">
          <input
            placeholder="请输入您的问题..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
          />
          <button onClick={handleSend} disabled={isLoading || !input.trim()}>
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  )
}

// ==========================================
// 3. 主程序 (Main Layout)
// ==========================================
function App() {
  const [currentView, setCurrentView] = useState('chat') // 'chat' | 'admin' | 'login'
  const [isAdminLoggedIn, setIsAdminLoggedIn] = useState(false)

  // 处理切换到管理页面的逻辑
  const handleSwitchToAdmin = () => {
    if (isAdminLoggedIn) {
      setCurrentView('admin')
    } else {
      setCurrentView('login')
    }
  }

  return (
    <div className="app-container">
      {/* 顶部导航 */}
      <header className="header" style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
        <div>
          <h1>🛡️ 敏宝守护者 Pro</h1>
          <p>您的专属儿科过敏营养顾问</p>
        </div>
        <div style={{display: 'flex', gap: '10px'}}>
          <button
            className={`nav-btn ${currentView === 'chat' ? 'active' : ''}`}
            onClick={() => setCurrentView('chat')}
          >
            <MessageSquare size={18} /> 对话
          </button>

          <button
            className={`nav-btn ${currentView === 'admin' || currentView === 'login' ? 'active' : ''}`}
            onClick={handleSwitchToAdmin}
          >
            {isAdminLoggedIn ? <Settings size={18} /> : <KeyRound size={18} />}
            {isAdminLoggedIn ? '管理' : '登录'}
          </button>
        </div>
      </header>

      {/* 视图路由逻辑 */}
      {currentView === 'chat' && <ChatView />}

      {currentView === 'admin' && <AdminView />}

      {currentView === 'login' && (
        <AdminLogin
          onLogin={(success) => {
            if (success) {
              setIsAdminLoggedIn(true)
              setCurrentView('admin')
            }
          }}
          onCancel={() => setCurrentView('chat')}
        />
      )}
    </div>
  )
}

export default App