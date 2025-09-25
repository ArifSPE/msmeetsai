import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Dashboard, Rules, Analyze, Execute, Chat } from './pages';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/rules" element={<Rules />} />
          <Route path="/analyze" element={<Analyze />} />
          <Route path="/execute" element={<Execute />} />
          <Route path="/chat" element={<Chat />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
