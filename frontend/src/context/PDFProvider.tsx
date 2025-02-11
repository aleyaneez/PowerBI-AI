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
  const [company, setCompany] = useState("");
  const [week, setWeek] = useState("");
  const [pdfName, setPdfName] = useState("");

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
        company,
        setCompany,
        week,
        setWeek,
        pdfName,
        setPdfName,
      }}
    >
      {children}
    </PDFContext.Provider>
  );
};

export default PDFProvider;