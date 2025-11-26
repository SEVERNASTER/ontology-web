import { useState } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import SearchResults from './components/SearchResults';
import DetailModal from './components/DetailModal';
import ListView from './components/ListView';
import './App.css';

const API_BASE = 'http://127.0.0.1:8000';

function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [searchResults, setSearchResults] = useState(null);
  const [selectedItem, setSelectedItem] = useState(null);
  const [listType, setListType] = useState(null);
  const [isSearching, setIsSearching] = useState(false);

  const handleSearch = async (query, category, onlineMode) => {
    setIsSearching(true);
    try {
      const endpoint = onlineMode ? '/buscador/online' : '/buscador';
      const params = new URLSearchParams({ q: query });
      if (category && category !== 'Todo' && !onlineMode) {
        params.append('clase', category);
      }
      
      const response = await fetch(`${API_BASE}${endpoint}?${params}`);
      const data = await response.json();
      
      setSearchResults(data);
      setCurrentView('search');
    } catch (error) {
      console.error('Error en búsqueda:', error);
      setSearchResults({ cantidad: 0, resultados: [] });
    } finally {
      setIsSearching(false);
    }
  };

  const handleViewList = (type) => {
    setListType(type);
    setCurrentView('list');
  };

  const handleItemClick = async (itemId) => {
    try {
      const response = await fetch(`${API_BASE}/individuos/${itemId}`);
      const data = await response.json();
      setSelectedItem(data);
    } catch (error) {
      console.error('Error cargando detalle:', error);
    }
  };

  const handleCloseModal = () => {
    setSelectedItem(null);
  };

  const handleNavigateToItem = async (itemId) => {
    handleCloseModal();
    setTimeout(() => handleItemClick(itemId), 100);
  };

  return (
    <div className="app">
      <Navbar 
        onSearch={handleSearch}
        onNavigate={(view) => {
          setCurrentView(view);
          setSearchResults(null);
        }}
        onViewList={handleViewList}
      />
      
      <main className="main-content">
        {currentView === 'dashboard' && (
          <Dashboard 
            onViewList={handleViewList}
            onItemClick={handleItemClick}
          />
        )}
        
        {currentView === 'search' && (
          <SearchResults 
            results={searchResults}
            onItemClick={handleItemClick}
            isSearching={isSearching}
          />
        )}
        
        {currentView === 'list' && listType && (
          <ListView 
            type={listType}
            onItemClick={handleItemClick}
          />
        )}
      </main>

      {selectedItem && (
        <DetailModal 
          item={selectedItem}
          onClose={handleCloseModal}
          onNavigate={handleNavigateToItem}
        />
      )}
    </div>
  );
}

export default App;