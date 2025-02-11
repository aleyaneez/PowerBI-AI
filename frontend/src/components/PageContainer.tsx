import React, { useContext } from 'react';
import { PDFContext } from '../context/PDFContext';
import ObservationCard from './ObservationCard';

interface PageContainerProps {
  pageNumber: number;
  pngUrl: string;
  observation: string;
  excluded: boolean;
}

const PageContainer: React.FC<PageContainerProps> = ({
  pageNumber,
  pngUrl,
  observation,
  excluded
}) => {
  const {
    setObservations,
    company,
    week,
    pdfName,
  } = useContext(PDFContext);

  // Aprobar
  const handleApprove = () => {
    setObservations(prev =>
      prev.map(obs =>
        obs.pageNumber === pageNumber
          ? { ...obs, approved: true }
          : obs
      )
    );
    console.log(`Observación de página ${pageNumber} aprobada`);
  };

  const handleEdit = (newValue: string) => {
    setObservations(prev =>
      prev.map(obs =>
        obs.pageNumber === pageNumber
          ? { ...obs, observation: newValue }
          : obs
      )
    );
    console.log(`Observación de página ${pageNumber} editada:`, newValue);
  };

  // Eliminar
  const handleDelete = () => {
    setObservations(prev =>
      prev.map(obs =>
        obs.pageNumber === pageNumber
          ? { ...obs, observation: "" }
          : obs
      )
    );
    console.log(`Observación de página ${pageNumber} eliminada`);
  };

  // Regenerar
  const handleRegenerate = async () => {
    try {
      const formData = new FormData();
      formData.append("company", company);
      console.log("Company:", company);
      formData.append("week", week);
      console.log("Week:", week);
      formData.append("pdfName", pdfName);
      console.log("PdfName:", pdfName);
      formData.append("pageNumber", pageNumber.toString());

      const res = await fetch("http://localhost:8000/regenerate-observation", {
        method: "POST",
        body: formData
      });
      if (!res.ok) throw new Error("Error al regenerar observación");

      const data = await res.json();
      setObservations(prev =>
        prev.map(obs =>
          obs.pageNumber === data.pageNumber
            ? { ...obs, observation: data.newObservation }
            : obs
        )
      );
      console.log(`Observación de página ${pageNumber} regenerada`);
    } catch (error) {
      console.error(error);
      alert("Error al regenerar la observación.");
    }
  };

  return (
    <div className="min-w-[300px]">
      <h3 className="text-center font-semibold text-tertiary mb-1">
        Página {pageNumber}
      </h3>
      <div className="p-2 flex justify-center items-center">
        <img
          src={pngUrl}
          alt={`Página ${pageNumber}`}
          width={900}
          className="border rounded-sm border-slate-400"
        />
      </div>
      {!excluded && (
        <ObservationCard
          observation={observation}
          onApprove={handleApprove}
          onDelete={handleDelete}
          onRegenerate={handleRegenerate}
          onEdit={handleEdit}
        />
      )}
    </div>
  );
};

export default PageContainer;