import { useEffect, useState } from 'react';
import './Dashboard.css';

const API_BASE = 'http://127.0.0.1:8000';

function Dashboard({ onViewList, onItemClick }) {
    const [stats, setStats] = useState({
        libros: 0,
        estudiantes: 0,
        docentes: 0,
        revistas: 0,
        bibliotecarios: 0
    });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadStats();
        // console.log(stats);
        
    }, []);

    const loadStats = async () => {
        try {
            const [libros, estudiantes, docentes, revistas, bibliotecarios] = await Promise.all([
                fetch(`${API_BASE}/libros`).then(r => r.json()),
                fetch(`${API_BASE}/estudiantes`).then(r => r.json()),
                fetch(`${API_BASE}/docentes`).then(r => r.json()),
                fetch(`${API_BASE}/revistas`).then(r => r.json()),
                fetch(`${API_BASE}/bibliotecarios`).then(r => r.json())
            ]);

            // console.log(libros, estudiantes, doce);
            

            setStats({
                libros: libros.length,
                estudiantes: estudiantes.length,
                docentes: docentes.length,
                revistas: revistas.length,
                bibliotecarios: bibliotecarios.length
            });

        } catch (error) {
            console.error('Error cargando estadísticas:', error);
        } finally {
            setLoading(false);
        }
    };

    const categories = [
        {
            id: 'libros',
            title: 'Libros',
            icon: '📖',
            count: 202,
            color: 'blue',
            gradient: 'linear-gradient(135deg, var(--neon-blue), var(--neon-purple))'
        },
        {
            id: 'estudiantes',
            title: 'Estudiantes',
            icon: '🎓',
            count: 100,
            color: 'pink',
            gradient: 'linear-gradient(135deg, var(--neon-pink), var(--neon-purple))'
        },
        {
            id: 'docentes',
            title: 'Docentes',
            icon: '👨‍🏫',
            count: 50,
            color: 'purple',
            gradient: 'linear-gradient(135deg, var(--neon-purple), var(--neon-blue))'
        },
        /** 
        {
            id: 'revistas',
            title: 'Revistas',
            icon: '📰',
            count: stats.revistas,
            color: 'green',
            gradient: 'linear-gradient(135deg, var(--neon-green), var(--neon-blue))'
        },*/
        {
            id: 'bibliotecarios',
            title: 'Bibliotecarios',
            icon: '👤',
            count: 20,
            color: 'yellow',
            gradient: 'linear-gradient(135deg, var(--neon-yellow), var(--neon-pink))'
        }
    ];

    if (loading) {
        return (
            <div className="dashboard-loading">
                <div className="loading-spinner"></div>
                <p>Cargando datos de la biblioteca...</p>
            </div>
        );
    }

    return (
        <div className="dashboard">
            <div className="dashboard-header">
                <h1 className="dashboard-title glow-text">
                    Panel de Control
                </h1>
                <p className="dashboard-subtitle">
                    Sistema de gestión bibliográfica basado en ontologías
                </p>
            </div>

            <div className="stats-grid">
                {/* {console.log(categories)} */}
                {categories.map((category, index) => (
                    <div
                        key={category.id}
                        className={`stat-card stat-card-${category.color} fade-in`}
                        style={{ animationDelay: `${index * 0.1}s` }}
                        onClick={() => onViewList(category.id)}
                    >
                        <div className="stat-card-background" style={{ background: category.gradient }}></div>
                        <div className="stat-card-content">
                            <div className="stat-icon">{category.icon}</div>
                            <div className="stat-info">
                                <div className="stat-count">{category.count}</div>
                                <div className="stat-label">{category.title}</div>
                            </div>
                        </div>
                        <div className="stat-card-hover">
                            <span>Ver todos →</span>
                        </div>
                    </div>
                ))}
            </div>

            <div className="dashboard-info">
                <div className="info-card fade-in" style={{ animationDelay: '0.5s' }}>
                    <h3 className="info-title">
                        <span className="info-icon">ℹ️</span>
                        Acerca del Sistema
                    </h3>
                    <p className="info-text">
                        Esta aplicación utiliza una ontología OWL para organizar y relacionar
                        la información de la biblioteca. Explora libros, autores, estudiantes
                        y sus interconexiones de manera intuitiva.
                    </p>
                </div>

                <div className="info-card fade-in" style={{ animationDelay: '0.6s' }}>
                    <h3 className="info-title">
                        <span className="info-icon">🔍</span>
                        Búsqueda Inteligente
                    </h3>
                    <p className="info-text">
                        Usa la barra de búsqueda superior para encontrar cualquier elemento
                        en la base de datos. Puedes filtrar por categoría o buscar en todo el sistema.
                    </p>
                </div>

                <div className="info-card fade-in" style={{ animationDelay: '0.7s' }}>
                    <h3 className="info-title">
                        <span className="info-icon">🔗</span>
                        Navegación Relacional
                    </h3>
                    <p className="info-text">
                        Haz clic en cualquier elemento para ver sus detalles y relaciones.
                        Las relaciones son navegables: puedes saltar de un libro a su autor
                        con un solo clic.
                    </p>
                </div>
            </div>
        </div>
    );
}

export default Dashboard;