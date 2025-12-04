import React, { useState, useEffect, useCallback } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import io from 'socket.io-client';
import axios from 'axios';
import './App.css';

// Components
import Login from './pages/Login';
import TaskDashboard from './pages/TaskDashboard';
import Navbar from './components/Navbar';
import TaskBoard from './components/TaskBoard';
import TaskForm from './components/TaskForm';

const API_URL = 'http://localhost:8000/api/v1';
const SOCKET_URL = 'http://localhost:8000';

function App() {
  const [user, setUser] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [socket, setSocket] = useState(null);
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState(null);

  // Check if user is logged in
  useEffect(() => {
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    if (token && userData) {
      setUser(JSON.parse(userData));
      // Set default axios header
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
  }, []);

  // Initialize WebSocket connection
  useEffect(() => {
    if (user) {
      const newSocket = io(SOCKET_URL, {
        auth: { token: localStorage.getItem('token') }
      });

      newSocket.on('connect', () => {
        console.log('Connected to WebSocket');
      });

      newSocket.on('task:created', (data) => {
        setTasks(prev => [data, ...prev]);
        showNotification('New task created', 'success');
      });

      newSocket.on('task:updated', (data) => {
        setTasks(prev => prev.map(t => t._id === data._id ? data : t));
        showNotification('Task updated', 'info');
      });

      newSocket.on('task:deleted', (data) => {
        setTasks(prev => prev.filter(t => t._id !== data.task_id));
        showNotification('Task deleted', 'info');
      });

      setSocket(newSocket);
      return () => newSocket.close();
    }
  }, [user]);

  // Fetch tasks
  const fetchTasks = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/tasks`);
      setTasks(response.data.data);
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
      showNotification('Failed to load tasks', 'error');
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  // Create task
  const handleCreateTask = async (taskData) => {
    try {
      const response = await axios.post(`${API_URL}/tasks`, taskData);
      setTasks(prev => [response.data.data, ...prev]);
      showNotification('Task created successfully', 'success');
    } catch (error) {
      console.error('Failed to create task:', error);
      showNotification('Failed to create task', 'error');
    }
  };

  // Update task
  const handleUpdateTask = async (taskId, updates) => {
    try {
      const response = await axios.put(`${API_URL}/tasks/${taskId}`, updates);
      setTasks(prev => prev.map(t => t._id === taskId ? response.data.data : t));
      showNotification('Task updated successfully', 'success');
    } catch (error) {
      console.error('Failed to update task:', error);
      showNotification('Failed to update task', 'error');
    }
  };

  // Delete task
  const handleDeleteTask = async (taskId) => {
    try {
      await axios.delete(`${API_URL}/tasks/${taskId}`);
      setTasks(prev => prev.filter(t => t._id !== taskId));
      showNotification('Task deleted successfully', 'success');
    } catch (error) {
      console.error('Failed to delete task:', error);
      showNotification('Failed to delete task', 'error');
    }
  };

  // Handle login
  const handleLogin = (userData, token) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    setUser(userData);
    showNotification(`Welcome, ${userData.full_name}!`, 'success');
  };

  // Handle logout
  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
    setTasks([]);
    if (socket) socket.close();
    showNotification('Logged out successfully', 'info');
  };

  // Show notification
  const showNotification = (message, type) => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 3000);
  };

  return (
    <Router>
      <div className="App">
        {user && <Navbar user={user} onLogout={handleLogout} />}
        
        <main className="app-main">
          {notification && (
            <div className={`notification notification-${notification.type}`}>
              {notification.message}
            </div>
          )}
          
          <Routes>
            <Route 
              path="/login" 
              element={user ? <Navigate to="/" /> : <Login onLogin={handleLogin} />} 
            />
            <Route
              path="/"
              element={
                user ? (
                  <TaskDashboard
                    tasks={tasks}
                    loading={loading}
                    onCreateTask={handleCreateTask}
                    onUpdateTask={handleUpdateTask}
                    onDeleteTask={handleDeleteTask}
                  />
                ) : (
                  <Navigate to="/login" />
                )
              }
            />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
