import React, { useEffect, useRef, useState } from 'react';
import Approve from './Approve';
import Delete from './Delete';
import Regenerate from './Regenerate';

interface ObservationCardProps {
  observation: string;
  approved: boolean;
  onApprove?: () => void;
  onRegenerate?: () => void;
  onDelete?: () => void;
  onEdit?: (newValue: string) => void;
}

const ObservationCard: React.FC<ObservationCardProps> = ({
  observation,
  approved = false,
  onApprove,
  onDelete,
  onRegenerate,
  onEdit,
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [draft, setDraft] = useState(observation);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    setDraft(observation);
  }, [observation]);

  const handleTextClick = () => {
    setIsEditing(true);
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setDraft(e.target.value);
  };

  const handleBlur = () => {
    if (onEdit) {
      onEdit(draft);
    }
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      textareaRef.current?.blur();
    }
  };

  const borderColor = approved ? 'border-emerald-600' : 'border-slate-400';

  return (
    <div className="flex flex-row items-center mt-4 justify-between">
      <div className={`p-4 border rounded-xl h-34 w-full text-primary ${borderColor}`}>
        {isEditing ? (
          <textarea
            ref={textareaRef}
            rows={3}
            className="w-full outline-none resize-none"
            value={draft}
            onChange={handleChange}
            onBlur={handleBlur}
            onKeyDown={handleKeyDown}
            autoFocus
          />
        ) : (
          <div
            onClick={handleTextClick}
            style={{ cursor: 'text', minHeight: '100%' }}
          >
            {draft || 'Sin observación'}
          </div>
        )}
      </div>
      
      {/* Botones de acción (Aprobar, Eliminar, Regenerar) */}
      <div className="flex flex-col items-center justify-center gap-2 ml-4">
        <Approve onClick={onApprove} />
        <Delete onClick={onDelete} />
        <Regenerate onClick={onRegenerate} />
      </div>
    </div>
  );
};

export default ObservationCard;