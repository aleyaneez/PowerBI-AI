import React from 'react';
import { Pencil } from 'lucide-react';
import Button from './Button';

interface EditProps {
  onClick?: () => void;
}

const Edit: React.FC<EditProps> = ({ onClick }) => {
  return (
    <Button
      text=""
      onClick={onClick}
      className="px-2 py-2"
      icon={<Pencil size={16} />}
      title="Editar observación"
    />
  );
};

export default Edit;