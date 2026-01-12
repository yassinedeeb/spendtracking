import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Dashboard() {
  const [spendingData, setSpendingData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('/api/spending');
        setSpendingData(response.data);
      } catch (err) {
        setError('Error fetching spending data.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="Dashboard">
      <h2>Monthly Spending Dashboard</h2>
      {spendingData && Object.keys(spendingData).length > 0 ? (
        <table>
          <thead>
            <tr>
              <th>Month</th>
              <th>Total Spending</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(spendingData).map(([month, total]) => (
              <tr key={month}>
                <td>{month}</td>
                <td>${total.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p>No spending data available.</p>
      )}
    </div>
  );
}

export default Dashboard;
