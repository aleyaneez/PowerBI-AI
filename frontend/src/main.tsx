import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './styles/globals.css'
import App from './App.tsx'
import PDFProvider from './context/PDFProvider.tsx'
import { pdfjs } from 'react-pdf';
pdfjs.GlobalWorkerOptions.workerSrc = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.10.38/pdf.min.mjs";

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <PDFProvider>
      <App />
    </PDFProvider>
  </StrictMode>,
)