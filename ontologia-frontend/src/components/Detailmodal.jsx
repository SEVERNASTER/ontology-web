import './DetailModal.css';

function DetailModal({ item, onClose, onNavigate }) {
    if (!item) return null;

    const extractIdFromRelation = (relationText) => {
        const match = relationText.match(/\(ID:\s*([^)]+)\)/);
        return match ? match[1] : null;
    };

    const getBadgeClass = (clase) => {
        const claseLower = clase?.toLowerCase() || '';
        if (claseLower.includes('libro')) return 'badge-libro';
        if (claseLower.includes('estudiante')) return 'badge-estudiante';
        if (claseLower.includes('docente')) return 'badge-docente';
        if (claseLower.includes('autor')) return 'badge-autor';
        if (claseLower.includes('editorial')) return 'badge-editorial';
        if (claseLower.includes('revista')) return 'badge-revista';
        if (claseLower.includes('bibliotecario')) return 'badge-bibliotecario';
        return 'badge-libro';
    };

    const getIcon = (clase) => {
        const claseLower = clase?.toLowerCase() || '';
        if (claseLower.includes('libro')) return '📖';
        if (claseLower.includes('estudiante')) return '🎓';
        if (claseLower.includes('docente')) return '👨‍🏫';
        if (claseLower.includes('autor')) return '✍️';
        if (claseLower.includes('editorial')) return '🏢';
        if (claseLower.includes('revista')) return '📰';
        if (claseLower.includes('bibliotecario')) return '👤';
        return '📄';
    };

    const formatKey = (key) => {
        return key
            .replace(/_/g, ' ')
            .replace(/\b\w/g, l => l.toUpperCase());
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <button className="modal-close" onClick={onClose}>
                    ✕
                </button>

                <div className="modal-header">
                    <div className="modal-icon">{getIcon(item.clase)}</div>
                    <div className="modal-title-wrapper">
                        <h2 className="modal-title glow-text">{item.nombre}</h2>
                        <span className={`badge ${getBadgeClass(item.clase)}`}>
                            {item.clase}
                        </span>
                    </div>
                </div>

                <div className="modal-body">
                    {/* Sección de Datos */}
                    {item.datos && Object.keys(item.datos).length > 0 && (
                        <div className="detail-section">
                            <h3 className="section-title">
                                <span className="section-icon">📋</span>
                                Información General
                            </h3>
                            <div className="detail-grid">
                                {Object.entries(item.datos).map(([key, values]) => (
                                    <div key={key} className="detail-item fade-in">
                                        <div className="detail-label">{formatKey(key)}</div>
                                        <div className="detail-value">
                                            {Array.isArray(values)
                                                ? values.map((val, idx) => (
                                                    <span key={idx} className="detail-value-chip">
                                                        {val}
                                                    </span>
                                                ))
                                                : values
                                            }
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Sección de Relaciones */}
                    {item.relaciones && Object.keys(item.relaciones).length > 0 && (
                        <div className="detail-section">
                            <h3 className="section-title">
                                <span className="section-icon">🔗</span>
                                Relaciones
                            </h3>
                            <div className="relations-grid">
                                {Object.entries(item.relaciones).map(([key, values]) => (
                                    <div key={key} className="relation-group fade-in">
                                        <div className="relation-type">{formatKey(key)}</div>
                                        <div className="relation-items">
                                            {Array.isArray(values)
                                                ? values.map((val, idx) => {
                                                    const id = extractIdFromRelation(val);
                                                    const displayText = val.replace(/\s*\(ID:.*?\)/, '');

                                                    return (
                                                        <button
                                                            key={idx}
                                                            className="relation-chip"
                                                            onClick={() => id && onNavigate(id)}
                                                            disabled={!id}
                                                        >
                                                            <span className="relation-text">{displayText}</span>
                                                            {id && (
                                                                <span className="relation-arrow">→</span>
                                                            )}
                                                        </button>
                                                    );
                                                })
                                                : values
                                            }
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Si no hay datos ni relaciones */}
                    {(!item.datos || Object.keys(item.datos).length === 0) &&
                        (!item.relaciones || Object.keys(item.relaciones).length === 0) && (
                            <div className="no-data">
                                <div className="no-data-icon">📭</div>
                                <p>No hay información adicional disponible para este elemento</p>
                            </div>
                        )}
                </div>

                <div className="modal-footer">
                    <button className="btn btn-secondary" onClick={onClose}>
                        Cerrar
                    </button>
                </div>
            </div>
        </div>
    );
}

export default DetailModal;