import React from 'react';
import { render } from 'react-dom';
import { createStore } from 'redux';
import { applyMiddleware } from 'redux';
import { compose } from 'redux';
import thunk from 'redux-thunk';
import { createLogger } from 'redux-logger';

import { Provider } from 'react-redux';
import { AuthProvider } from './context/AuthContext';

import { Reducer } from './master-reducer.js';
import { App } from './app';

// clear cache when app first starts (page refresh)
window.sessionStorage.clear();

// redux state logger
const logger = createLogger({
  collapsed: true
});

// create global state store
export const store = createStore(
  Reducer,
  compose(applyMiddleware(thunk, logger))
);

// render/run app
render(
  <Provider store={store}>
    <AuthProvider> {/* Wrap the app with AuthProvider */}
      <App />
    </AuthProvider>
  </Provider>,
  document.getElementById('root')
);

// Add this after store creation
const setInitialWidth = () => {
  const windowWidth = window.innerWidth;
  store.dispatch({
    type: 'SET_WIDTH',
    payload: windowWidth
  });
};

// Add window resize listener
window.addEventListener('resize', setInitialWidth);

// Initial call
setInitialWidth();
