import React, { useContext } from 'react';
import { PDFContext } from "../context/PDFContext";
import Button from './Button';
import { FileDown } from 'lucide-react';

interface ExportButtonProps {
  company: string;
  week: string;
}

const ExportButton: React.FC<ExportButtonProps> = ({ company, week }) => {
  const { pdfFile, observations } = useContext(PDFContext);

  const handleExport = async () => {
    if (!pdfFile) {
      alert("No hay PDF cargado.");
      return;
    }
    const obsJSON = JSON.stringify(observations);

    const rawCompany = company;
    const rawWeek = week;

    const formData = new FormData();
    formData.append("company", rawCompany);
    formData.append("week", rawWeek);
    formData.append("pdfName", rawCompany);
    formData.append("obsJSON", obsJSON);

    try {
      const res = await fetch("http://localhost:8000/apply-observations", {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        throw new Error("Error al aplicar observaciones");
      }
      const data = await res.json();
      if (data.final_pdf_url) {
        window.open(data.final_pdf_url, "_blank");
      } else {
        alert("No se recibió una URL final de PDF");
      }
    } catch (error) {
      console.error("Error en handleExport:", error);
      alert("Error al generar el PDF final.");
    }
  };

  return (
    <div>
      <Button
        text="Exportar PDF"
        onClick={handleExport}
        className="gap-2 px-10 py-4"
        icon={<FileDown size={20} />}
      />
    </div>
  );
};

export default ExportButton;