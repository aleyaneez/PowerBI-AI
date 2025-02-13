import React, { useContext, useState } from 'react';
import { PDFContext } from "../context/PDFContext";
import Button from './Button';
import ConfirmationDialog from './ConfirmationDialog';
import { FileDown } from 'lucide-react';

interface ExportButtonProps {
  company: string;
  week: string;
}

const ExportButton: React.FC<ExportButtonProps> = ({ company, week }) => {
  const { pdfFile, observations, excludes } = useContext(PDFContext);
  const [showDialog, setShowDialog] = useState(false);

  const exportPdf = async () => {
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

  const unapprovedCount = observations
    .filter(obs => !excludes.includes(obs.pageNumber - 1))
    .filter(obs => !obs.approved)
    .length;

  const allApproved = unapprovedCount === 0;

  const messageBody = unapprovedCount === 1
    ? <>¿Estás seguro que quieres exportar? Queda <strong>una</strong> observación sin aprobar.</>
    : <>¿Estás seguro que quieres exportar? Quedan <strong>{unapprovedCount}</strong> observaciones sin aprobar.</>;

    const handleExport = () => {
      if (allApproved) {
        exportPdf();
      } else {
        setShowDialog(true);
      }
    };

    const handleConfirm = () => {
      setShowDialog(false);
      exportPdf();
    };

    const handleCancel = () => {
      setShowDialog(false);
    };

  return (
    <div>
      <Button
        text="Exportar PDF"
        onClick={handleExport}
        className="gap-2 px-10 py-4"
        icon={<FileDown size={20} />}
      />


      {showDialog && (
        <ConfirmationDialog
          message={messageBody}
          onConfirm={handleConfirm}
          onCancel={handleCancel}
        />
      )}
    </div>
  );
};

export default ExportButton;