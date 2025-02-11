import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './styles/globals.css'
import App from './App.tsx'
import PDFProvider from './context/PDFProvider.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <PDFProvider>
      <App />
    </PDFProvider>
  </StrictMode>,
)