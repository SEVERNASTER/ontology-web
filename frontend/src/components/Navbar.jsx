import { useState } from 'react';
import './Navbar.css';

function Navbar({ onSearch, onNavigate, onViewList }) {
    const [searchQuery, setSearchQuery] = useState('');
    const [searchCategory, setSearchCategory] = useState('Todo');
    const [menuOpen, setMenuOpen] = useState(false);
    const [onlineMode, setOnlineMode] = useState(false);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (searchQuery.trim()) {
            onSearch(searchQuery, searchCategory, onlineMode);
            setMenuOpen(false);
        }
    };

    return (
        <nav className="navbar">
            <div className="navbar-container">
                <div className="navbar-brand" onClick={() => onNavigate('dashboard')}>
                    <span className="brand-icon">📚</span>
                    <span className="brand-text glow-text">BiblioOntología</span>
                </div>

                <form className="search-form" onSubmit={handleSubmit}>
                    <select
                        className="search-category"
                        value={searchCategory}
                        onChange={(e) => setSearchCategory(e.target.value)}
                    >
                        <option value="Todo">Todo</option>
                        <option value="Libro">Libros</option>
                        <option value="Estudiante">Estudiantes</option>
                        <option value="Docente">Docentes</option>
                        <option value="Autor">Autores</option>
                        <option value="Editorial">Editoriales</option>
                    </select>

                    <input
                        type="text"
                        className="search-input"
                        placeholder="Buscar en la biblioteca..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />

                    <button type="submit" className="search-button">
                        <span className="search-icon">🔍</span>
                    </button>

                    <div className="online-toggle">
                        <input
                            type="checkbox"
                            id="online-mode"
                            className="toggle-checkbox"
                            checked={onlineMode}
                            onChange={(e) => setOnlineMode(e.target.checked)}
                        />
                        <label htmlFor="online-mode" className="toggle-label">
                            <span className="toggle-inner"></span>
                            <span className="toggle-switch"></span>
                        </label>
                        <span className="toggle-text">
                            {onlineMode ? '🌐 DBpedia' : '💾 Local'}
                        </span>
                    </div>
                </form>

                <button
                    className="menu-toggle"
                    onClick={() => setMenuOpen(!menuOpen)}
                >
                    ☰
                </button>

                <div className={`navbar-menu ${menuOpen ? 'active' : ''}`}>
                    <button
                        className="nav-link"
                        onClick={() => {
                            onNavigate('dashboard');
                            setMenuOpen(false);
                        }}
                    >
                        Dashboard
                    </button>
                    <button
                        className="nav-link"
                        onClick={() => {
                            onViewList('libros');
                            setMenuOpen(false);
                        }}
                    >
                        Libros
                    </button>
                    <button
                        className="nav-link"
                        onClick={() => {
                            onViewList('estudiantes');
                            setMenuOpen(false);
                        }}
                    >
                        Estudiantes
                    </button>
                    <button
                        className="nav-link"
                        onClick={() => {
                            onViewList('docentes');
                            setMenuOpen(false);
                        }}
                    >
                        Docentes
                    </button>
                    <button
                        className="nav-link"
                        onClick={() => {
                            onViewList('revistas');
                            setMenuOpen(false);
                        }}
                    >
                        Revistas
                    </button>
                    <button
                        className="nav-link"
                        onClick={() => {
                            onViewList('bibliotecarios');
                            setMenuOpen(false);
                        }}
                    >
                        Bibliotecarios
                    </button>
                </div>
            </div>
        </nav>
    );
}

export default Navbar;