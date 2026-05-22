import './App.css';
import Routers from './router';
import Toast from './components/Toast/Toast';


function App() {
  console.log(process.env.REACT_APP_MODE)
  return (
    <div className="App">
        <Toast/>
        <Routers></Routers>
    </div>
  );
}

export default App;
