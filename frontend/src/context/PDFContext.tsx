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
  excludes: number[];
  setExcludes: React.Dispatch<React.SetStateAction<number[]>>;
  pngUrls: string[];
  setPngUrls: React.Dispatch<React.SetStateAction<string[]>>;
}

export const PDFContext = createContext<PDFContextProps>({
  pdfFile: null,
  setPdfFile: () => {},
  observations: [],
  setObservations: () => {},
  excludes: [],
  setExcludes: () => {},
  pngUrls: [],
  setPngUrls: () => {},
});