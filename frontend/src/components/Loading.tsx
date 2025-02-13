import React from 'react';
import PropagateLoader from 'react-spinners/PropagateLoader';

interface LoadingProps {
    color?: string;
    size?: number;
};

const Loading: React.FC<LoadingProps> = ({color, size}) => {
    return (
        <div className="flex justify-center items-center">
            <PropagateLoader color={color} size={size} />
        </div>
    );
};

export default Loading;