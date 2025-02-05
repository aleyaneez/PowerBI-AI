import React, { useState, ReactNode } from "react";
import { PDFContext, PageObservation } from "./PDFContext";

interface PDFProviderProps {
  children: ReactNode;
}

const PDFProvider: React.FC<PDFProviderProps> = ({ children }) => {
  const [pdfFile, setPdfFile] = useState<string | null>(null);
  const [observations, setObservations] = useState<PageObservation[]>([]);

  return (
    <PDFContext.Provider value={{ pdfFile, setPdfFile, observations, setObservations }}>
      {children}
    </PDFContext.Provider>
  );
};

export default PDFProvider;