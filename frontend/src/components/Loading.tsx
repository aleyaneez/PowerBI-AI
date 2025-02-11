import React from 'react';
import 'ldrs/bouncy';

const Loading: React.FC = () => {
    return (
        <div className="flex flex-col justify-center items-center">
            <l-bouncy size="45" speed="1.75" color="indigo"></l-bouncy>
        </div>
    );
};

export default Loading;