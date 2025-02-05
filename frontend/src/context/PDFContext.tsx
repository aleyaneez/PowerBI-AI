import { createContext } from "react";

export interface PageObservation {
  pageNumber: number;
  observation: string;
  approved: boolean;
}

export interface PDFContextProps {
  pdfFile: string | null;
  setPdfFile: React.Dispatch<React.SetStateAction<string | null>>;
  observations: PageObservation[];
  setObservations: React.Dispatch<React.SetStateAction<PageObservation[]>>;
}

export const PDFContext = createContext<PDFContextProps>({
  pdfFile: null,
  setPdfFile: () => {},
  observations: [],
  setObservations: () => {},
});