import React, { useState, ReactNode } from "react";
import { PDFContext, PageObservation } from "./PDFContext";

interface PDFProviderProps {
  children: ReactNode;
}

const PDFProvider: React.FC<PDFProviderProps> = ({ children }) => {
  const [pdfFile, setPdfFile] = useState<string | null>(null);
  const [observations, setObservations] = useState<PageObservation[]>([]);
  const [excludes, setExcludes] = useState<number[]>([]);
  const [pngUrls, setPngUrls] = useState<string[]>([]);

  return (
    <PDFContext.Provider
      value={{
        pdfFile,
        setPdfFile,
        observations,
        setObservations,
        excludes,
        setExcludes,
        pngUrls,
        setPngUrls,
      }}
    >
      {children}
    </PDFContext.Provider>
  );
};

export default PDFProvider;