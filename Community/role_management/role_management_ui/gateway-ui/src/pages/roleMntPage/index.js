import ReactDOM from 'react-dom';
import { SimplePage } from '@bluecat/limani';
import App from './App';

ReactDOM.render(
    <SimplePage pageTitle='DNS Role Management'>
        <App />
    </SimplePage>,
    document.getElementById('root'),
);
