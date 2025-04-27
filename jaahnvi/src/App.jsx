import { useState } from 'react'
import AuthPage from './components/auth/authpage'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <AuthPage />
    </>
  )
}

export default App
