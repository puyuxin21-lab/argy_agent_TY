import { useState, useRef, useEffect } from 'react'
import { Send, User, Bot, Loader2 } from 'lucide-react'
import './App.css'

function App() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState([
    { role: 'assistant', content: '您好呀！我是敏宝守护者。宝宝最近有什么过敏问题吗？💕' }
  ])
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)

  // 自动滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }
  useEffect(scrollToBottom, [messages])

  // 发送消息处理
  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userQuestion = input
    setInput('') // 清空输入框
    setIsLoading(true)

    // 1. 添加用户消息到界面
    setMessages(prev => [...prev, { role: 'user', content: userQuestion }])

    try {
      // 2. 发送请求给后端 FastAPI
      const response = await fetch('http://127.0.0.1:8000/api/v1/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: userQuestion }),
      })

      const data = await response.json()

      // 3. 添加 AI 回答到界面
      if (response.ok) {
        setMessages(prev => [...prev, { role: 'assistant', content: data.answer }])
      } else {
        setMessages(prev => [...prev, { role: 'assistant', content: '⚠️ 出错了：无法连接到大脑。' }])
      }

    } catch (error) {
      console.error(error)
      setMessages(prev => [...prev, { role: 'assistant', content: '🚫 网络错误，请检查后端是否启动。' }])
    } finally {
      setIsLoading(false)
    }
  }

  // 支持回车发送
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="app-container">
      {/* 顶部标题栏 */}
      <header className="header">
        <h1>敏宝守护者 Pro</h1>
        <p>您的专属儿科过敏营养顾问</p>
      </header>

      {/* 聊天区域 */}
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

        {/* 加载中动画 */}
        {isLoading && (
          <div className="message-row bot-row">
            <div className="avatar assistant">
              <Bot size={20} />
            </div>
            <div className="bubble assistant loading-bubble">
              <Loader2 className="spinner" size={16} /> 正在思考...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* 底部输入框 */}
      <div className="input-area">
        <div className="input-wrapper">
          <input
            type="text"
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

export default App