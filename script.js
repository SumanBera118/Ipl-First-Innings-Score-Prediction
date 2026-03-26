document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('predictionForm');
    const predictBtn = document.getElementById('predictBtn');
    const resultsCard = document.getElementById('resultsCard');
    const loader = document.querySelector('.loader');
    const btnText = predictBtn.querySelector('span');

    // Team combinations validation
    const teamSelects = document.querySelectorAll('select[name="batting_team"], select[name="bowling_team"]');
    
    teamSelects.forEach(select => {
        select.addEventListener('change', function() {
            const battingTeam = document.querySelector('select[name="batting_team"]').value;
            const bowlingTeam = document.querySelector('select[name="bowling_team"]').value;
            
            if (battingTeam && bowlingTeam && battingTeam === bowlingTeam) {
                alert('Batting and bowling teams cannot be the same!');
                this.value = '';
            }
        });
    });

    // Auto-calculate run rate
    function calculateRunRate() {
        const runs = parseFloat(document.querySelector('input[name="runs"]').value) || 0;
        const overs = parseFloat(document.querySelector('input[name="overs"]').value) || 0.1;
        const runRateInput = document.querySelector('input[name="strike_rate"]');
        
        if (runRateInput && overs > 0) {
            const calculatedRR = (runs / overs).toFixed(1);
            runRateInput.value = calculatedRR;
        }
    }

    // Add event listeners for auto-calculation
    document.querySelector('input[name="runs"]').addEventListener('input', calculateRunRate);
    document.querySelector('input[name="overs"]').addEventListener('input', calculateRunRate);

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Show loading state
        predictBtn.disabled = true;
        btnText.style.opacity = '0.5';
        loader.style.display = 'inline-block';
        
        // Hide previous results
        resultsCard.style.display = 'none';
        
        // Collect form data
        const formData = new FormData(form);
        
        try {
            const response = await fetch('/predict', {
                method: 'POST',
                body: formData
            });
            
            const resultText = await response.text();
            console.log('Raw response:', resultText);
            
            // Parse the prediction
            const predictedScore = parseInt(resultText) || 150;
            
            // Update results
            updateResults(predictedScore);
            resultsCard.style.display = 'block';
            
            // Scroll to results
            resultsCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            
        } catch (error) {
            console.error('Error:', error);
            alert('Network error. Please try again.');
        } finally {
            // Reset loading state
            predictBtn.disabled = false;
            btnText.style.opacity = '1';
            loader.style.display = 'none';
        }
    });

    function updateResults(predictedScore) {
        // Animate score counting
        const scoreElement = document.getElementById('predictedScore');
        const targetScore = predictedScore;
        let currentScore = 0;
        
        // Clear any existing animation
        if (window.scoreInterval) {
            clearInterval(window.scoreInterval);
        }
        
        window.scoreInterval = setInterval(() => {
            if (currentScore < targetScore) {
                currentScore += Math.ceil(targetScore / 50);
                if (currentScore > targetScore) currentScore = targetScore;
                scoreElement.textContent = currentScore;
            } else {
                clearInterval(window.scoreInterval);
            }
        }, 20);
        
        // Calculate confidence based on overs completed
        const overs = parseFloat(document.querySelector('input[name="overs"]').value) || 5;
        const confidence = Math.min(95, Math.max(70, Math.floor(70 + (overs/20)*25)));
        
        // Calculate range
        const range_low = Math.max(0, predictedScore - 15);
        const range_high = predictedScore + 15;
        
        // Update stats
        document.getElementById('confidenceValue').textContent = confidence + '%';
        document.getElementById('scoreRange').textContent = `${range_low}-${range_high}`;
        
        // Animate confidence bar
        const confidenceFill = document.getElementById('confidenceFill');
        confidenceFill.style.width = '0%';
        
        setTimeout(() => {
            confidenceFill.style.width = confidence + '%';
        }, 100);
    }

    // Input validation
    document.querySelectorAll('input[type="number"]').forEach(input => {
        input.addEventListener('input', function() {
            const min = parseFloat(this.min) || 0;
            const max = parseFloat(this.max);
            let value = parseFloat(this.value) || 0;
            
            if (value < min) this.value = min;
            if (max && value > max) this.value = max;
            
            // Format overs input (keep one decimal)
            if (this.name === 'overs' && this.value.includes('.')) {
                const parts = this.value.split('.');
                if (parts[1] && parts[1].length > 1) {
                    this.value = parts[0] + '.' + parts[1].slice(0, 1);
                }
            }
        });
    });
});