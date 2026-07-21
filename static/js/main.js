document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const progressContainer = document.getElementById('progress-container');
    const progressFill = document.getElementById('progress-fill');
    const progressPercentage = document.getElementById('progress-percentage');
    const progressStatus = document.getElementById('progress-status');
    const dashboardSection = document.getElementById('dashboard-section');
    const uploadSection = document.getElementById('upload-section');
    
    // Meta elements
    const metaHolder = document.getElementById('meta-holder');
    const metaNumber = document.getElementById('meta-number');
    const metaCustid = document.getElementById('meta-custid');
    const metaType = document.getElementById('meta-type');
    const metaPeriod = document.getElementById('meta-period');
    
    // Stats elements
    const statTotalCredit = document.getElementById('stat-total-credit');
    const statTotalDebit = document.getElementById('stat-total-debit');
    const statNetFlow = document.getElementById('stat-net-flow');
    const statEndBalance = document.getElementById('stat-end-balance');
    
    // Table and Actions
    const tableBody = document.getElementById('table-body');
    const tableCount = document.getElementById('table-count');
    const currencySelect = document.getElementById('currency-select');
    const addRowBtn = document.getElementById('add-row-btn');
    const exportBtn = document.getElementById('export-btn');
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');

    // Search and Pagination Elements
    const searchInput = document.getElementById('search-input');
    const pageSizeSelect = document.getElementById('page-size-select');
    const prevPageBtn = document.getElementById('prev-page-btn');
    const nextPageBtn = document.getElementById('next-page-btn');
    const pageInfo = document.getElementById('page-info');

    // Password Modal Elements
    const passwordModal = document.getElementById('password-modal');
    const pdfPasswordInput = document.getElementById('pdf-password-input');
    const passwordError = document.getElementById('password-error');
    const cancelPasswordBtn = document.getElementById('cancel-password-btn');
    const submitPasswordBtn = document.getElementById('submit-password-btn');
    let activeFile = null;

    // Global state
    let currencySymbol = '₹';
    let allTransactions = []; // Holds the full list in memory
    let filteredTransactions = []; // Holds the searched/filtered subset
    let currentPage = 1;
    let pageSize = 15;
    let cashflowChart = null;

    // Drag and Drop Events
    dropZone.addEventListener('click', () => fileInput.click());
    
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });

    // Password Modal Actions
    cancelPasswordBtn.addEventListener('click', () => {
        passwordModal.style.display = 'none';
        pdfPasswordInput.value = '';
        handleError('Unlocking statement cancelled by user.');
    });

    submitPasswordBtn.addEventListener('click', () => {
        const pwd = pdfPasswordInput.value;
        if (!pwd) return;
        passwordModal.style.display = 'none';
        pdfPasswordInput.value = '';
        handleFileUpload(activeFile, pwd);
    });

    pdfPasswordInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            submitPasswordBtn.click();
        }
    });

    // Handle File Upload & Parse
    function handleFileUpload(file, password = null) {
        if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
            showToast('Please upload a valid PDF file.', 'error');
            return;
        }

        activeFile = file;
        const formData = new FormData();
        formData.append('file', file);
        if (password) {
            formData.append('password', password);
        }

        // Show progress UI
        progressContainer.style.display = 'block';
        updateProgress(0, 'Preparing upload...');

        // Perform Upload
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/api/upload', true);

        // Track upload progress
        xhr.upload.onprogress = (e) => {
            if (e.lengthComputable) {
                const percentComplete = Math.round((e.loaded / e.total) * 50); // Upload takes first 50%
                updateProgress(percentComplete, 'Uploading statement...');
            }
        };

        xhr.onload = function() {
            try {
                const response = JSON.parse(xhr.responseText);
                if (xhr.status === 200) {
                    if (response.success) {
                        updateProgress(100, 'Parsing complete!');
                        setTimeout(() => {
                            renderDashboard(response.metadata, response.transactions);
                            showToast('Statement successfully converted!', 'success');
                        }, 500);
                    } else {
                        handleError(response.error || 'Unknown parsing error occurred.');
                    }
                } else if (xhr.status === 400 && (response.error === 'PASSWORD_REQUIRED' || response.error === 'PASSWORD_INCORRECT')) {
                    // Hide progress UI and prompt for password
                    progressContainer.style.display = 'none';
                    updateProgress(0, '');
                    
                    if (response.error === 'PASSWORD_INCORRECT') {
                        passwordError.style.display = 'block';
                    } else {
                        passwordError.style.display = 'none';
                    }
                    
                    passwordModal.style.display = 'flex';
                    pdfPasswordInput.focus();
                } else {
                    handleError(response.error || `Server error (${xhr.status})`);
                }
            } catch (e) {
                handleError('Failed to parse server response.');
            }
        };

        xhr.onerror = function() {
            handleError('Network error occurred. Connection failed.');
        };

        xhr.send(formData);
    }

    function updateProgress(percentage, status) {
        progressFill.style.width = `${percentage}%`;
        progressPercentage.innerText = `${percentage}%`;
        progressStatus.innerText = status;
    }

    function handleError(msg) {
        showToast(msg, 'error');
        progressContainer.style.display = 'none';
        updateProgress(0, '');
    }

    // Render Dashboard & Setup Tables
    function renderDashboard(metadata, transactions) {
        // Populate metadata
        metaHolder.innerText = metadata.holder_name || '';
        metaNumber.innerText = metadata.account_number || '';
        metaCustid.innerText = metadata.customer_id || '';
        metaType.innerText = metadata.account_type || '';
        metaPeriod.innerText = metadata.statement_period || '';

        // Add internal unique ID to transactions for editing reference
        allTransactions = transactions.map((tx, idx) => ({
            id: idx,
            txn_date: tx.txn_date || '',
            value_date: tx.value_date || '',
            particulars: tx.particulars || '',
            ref_no: tx.ref_no || '',
            debit: tx.debit || '',
            credit: tx.credit || '',
            balance: tx.balance || ''
        }));

        filteredTransactions = [...allTransactions];
        currentPage = 1;

        // Hide upload section, show dashboard
        uploadSection.style.display = 'none';
        dashboardSection.style.display = 'grid';

        // Render table page and charts
        applyFiltersAndRender();
    }

    // Apply Filter & Render Table Page
    function applyFiltersAndRender() {
        const query = searchInput.value.toLowerCase().trim();
        
        if (!query) {
            filteredTransactions = [...allTransactions];
        } else {
            filteredTransactions = allTransactions.filter(tx => 
                tx.txn_date.toLowerCase().includes(query) ||
                tx.particulars.toLowerCase().includes(query) ||
                tx.ref_no.toLowerCase().includes(query) ||
                tx.debit.toLowerCase().includes(query) ||
                tx.credit.toLowerCase().includes(query)
            );
        }

        // Calculate pages
        const totalItems = filteredTransactions.length;
        let totalPages = 1;
        if (pageSize !== 'all') {
            totalPages = Math.ceil(totalItems / pageSize) || 1;
        }

        // Bound current page
        if (currentPage > totalPages) {
            currentPage = totalPages;
        }
        if (currentPage < 1) {
            currentPage = 1;
        }

        // Render Table Slice
        tableBody.innerHTML = '';
        
        let displayList = filteredTransactions;
        if (pageSize !== 'all') {
            const start = (currentPage - 1) * parseInt(pageSize);
            const end = start + parseInt(pageSize);
            displayList = filteredTransactions.slice(start, end);
        }

        displayList.forEach(tx => {
            appendRowToTable(tx);
        });

        // Update pagination buttons state
        prevPageBtn.disabled = currentPage === 1;
        nextPageBtn.disabled = pageSize === 'all' || currentPage === totalPages;
        pageInfo.innerText = pageSize === 'all' 
            ? `Showing all ${totalItems} transactions` 
            : `Page ${currentPage} of ${totalPages} (Showing ${displayList.length} of ${totalItems})`;

        recalculateSummary();
    }

    // Format utility
    function formatMoney(num) {
        return num.toLocaleString('en-IN', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }

    function parseNumericCell(val) {
        if (!val) return 0;
        const cleaned = val.replace(/[^\d.-]/g, '');
        const num = parseFloat(cleaned);
        return isNaN(num) ? 0 : num;
    }

    // Dynamic Summary Recalculations and Chart Redrawing
    function recalculateSummary() {
        let totalDebit = 0;
        let totalCredit = 0;
        let lastBalance = 0;

        // Calculate stats on the FULL in-memory transaction list (not just the current page!)
        allTransactions.forEach((tx, idx) => {
            const debit = parseNumericCell(tx.debit);
            const credit = parseNumericCell(tx.credit);
            const balance = parseNumericCell(tx.balance);

            totalDebit += debit;
            totalCredit += credit;
            
            if (idx === allTransactions.length - 1) {
                lastBalance = balance;
            }
        });

        const netFlow = totalCredit - totalDebit;

        // Update statistics DOM
        statTotalCredit.innerText = `${currencySymbol} ${formatMoney(totalCredit)}`;
        statTotalDebit.innerText = `${currencySymbol} ${formatMoney(totalDebit)}`;
        
        statNetFlow.innerText = `${netFlow >= 0 ? '+' : ''}${currencySymbol} ${formatMoney(netFlow)}`;
        if (netFlow >= 0) {
            statNetFlow.className = 'stat-value green';
        } else {
            statNetFlow.className = 'stat-value red';
        }

        statEndBalance.innerText = `${currencySymbol} ${formatMoney(lastBalance)}`;
        tableCount.innerText = `${allTransactions.length} transaction${allTransactions.length !== 1 ? 's' : ''} loaded`;

        // Update Interactive Chart
        updateCashflowChart();
    }

    // Update Chart.js Trendline
    function updateCashflowChart() {
        const ctx = document.getElementById('cashflow-chart').getContext('2d');
        
        // Take a max of 30 data points representing transactions to prevent chart clutter
        const step = Math.max(1, Math.ceil(allTransactions.length / 30));
        const chartTx = allTransactions.filter((_, idx) => idx % step === 0);
        
        const labels = chartTx.map(tx => tx.txn_date || '');
        const data = chartTx.map(tx => parseNumericCell(tx.balance));

        if (cashflowChart) {
            cashflowChart.destroy();
        }

        cashflowChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Running Balance',
                    data: data,
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3,
                    pointRadius: 2,
                    pointHoverRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#64748b', font: { size: 10 } }
                    },
                    y: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { 
                            color: '#64748b',
                            font: { size: 10 },
                            callback: function(value) {
                                return currencySymbol + ' ' + formatMoney(value);
                            }
                        }
                    }
                }
            }
        });
    }

    // Append single row to table element
    function appendRowToTable(tx) {
        const tr = document.createElement('tr');
        tr.dataset.id = tx.id;
        
        const txnDate = tx.txn_date || '';
        const valDate = tx.value_date || '';
        const particulars = tx.particulars || '';
        const refNo = tx.ref_no || '';
        
        // Convert to numbers if they are strings
        const debit = tx.debit ? formatMoney(parseNumericCell(tx.debit)) : '';
        const credit = tx.credit ? formatMoney(parseNumericCell(tx.credit)) : '';
        const balance = tx.balance ? formatMoney(parseNumericCell(tx.balance)) : '0.00';

        tr.innerHTML = `
            <td class="cell-editable text-center cell-date" contenteditable="true">${txnDate}</td>
            <td class="cell-editable text-center cell-val-date" contenteditable="true">${valDate}</td>
            <td class="cell-editable cell-particulars" contenteditable="true">${particulars}</td>
            <td class="cell-editable text-center cell-ref" contenteditable="true">${refNo}</td>
            <td class="cell-editable text-right cell-debit debit-val" contenteditable="true">${debit === '0.00' ? '' : debit}</td>
            <td class="cell-editable text-right cell-credit credit-val" contenteditable="true">${credit === '0.00' ? '' : credit}</td>
            <td class="cell-editable text-right cell-balance balance-val" contenteditable="true">${balance}</td>
            <td class="text-center">
                <button class="btn-danger btn-delete-row" title="Delete Row">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
                </button>
            </td>
        `;

        // Event listeners to capture editable changes back to memory state
        const editableCells = tr.querySelectorAll('.cell-editable');
        editableCells.forEach(cell => {
            cell.addEventListener('blur', () => {
                const targetTx = allTransactions.find(t => t.id === parseInt(tr.dataset.id));
                if (!targetTx) return;

                // Format cell display
                if (cell.classList.contains('cell-debit') || cell.classList.contains('cell-credit') || cell.classList.contains('cell-balance')) {
                    const num = parseNumericCell(cell.innerText);
                    if (num === 0 && (cell.classList.contains('cell-debit') || cell.classList.contains('cell-credit'))) {
                        cell.innerText = '';
                    } else {
                        cell.innerText = formatMoney(num);
                    }
                }

                // Update memory state
                if (cell.classList.contains('cell-date')) targetTx.txn_date = cell.innerText.trim();
                if (cell.classList.contains('cell-val-date')) targetTx.value_date = cell.innerText.trim();
                if (cell.classList.contains('cell-particulars')) targetTx.particulars = cell.innerText.trim();
                if (cell.classList.contains('cell-ref')) targetTx.ref_no = cell.innerText.trim();
                if (cell.classList.contains('cell-debit')) targetTx.debit = cell.innerText.trim();
                if (cell.classList.contains('cell-credit')) targetTx.credit = cell.innerText.trim();
                if (cell.classList.contains('cell-balance')) targetTx.balance = cell.innerText.trim();

                recalculateSummary();
            });
        });

        // Delete Row trigger
        tr.querySelector('.btn-delete-row').addEventListener('click', () => {
            const index = allTransactions.findIndex(t => t.id === parseInt(tr.dataset.id));
            if (index !== -1) {
                allTransactions.splice(index, 1);
            }
            tr.remove();
            applyFiltersAndRender();
            showToast('Row deleted', 'info');
        });

        tableBody.appendChild(tr);
    }

    // Add Row Button Action
    addRowBtn.addEventListener('click', () => {
        let newBalance = '0.00';
        if (allTransactions.length > 0) {
            newBalance = allTransactions[allTransactions.length - 1].balance;
        }

        const dateStr = new Date().toLocaleDateString('en-GB', {
            day: '2-digit',
            month: 'short',
            year: 'numeric'
        }).replace(/ /g, '-').toUpperCase(); // E.g., 20-JUL-2026

        const newId = allTransactions.length > 0 ? Math.max(...allTransactions.map(t => t.id)) + 1 : 0;
        const newTx = {
            id: newId,
            txn_date: dateStr,
            value_date: dateStr,
            particulars: 'New Manual Entry',
            ref_no: '-',
            debit: '',
            credit: '',
            balance: newBalance
        };

        allTransactions.push(newTx);
        
        // Recalculate and render last page to show the added row
        if (pageSize !== 'all') {
            currentPage = Math.ceil(allTransactions.length / pageSize) || 1;
        }
        applyFiltersAndRender();
        showToast('New row added', 'success');
    });

    // Search input trigger
    searchInput.addEventListener('input', () => {
        currentPage = 1;
        applyFiltersAndRender();
    });

    // Page size selection change
    pageSizeSelect.addEventListener('change', (e) => {
        pageSize = e.target.value;
        currentPage = 1;
        applyFiltersAndRender();
    });

    // Prev Page Button Action
    prevPageBtn.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            applyFiltersAndRender();
        }
    });

    // Next Page Button Action
    nextPageBtn.addEventListener('click', () => {
        const totalPages = pageSize === 'all' ? 1 : Math.ceil(filteredTransactions.length / pageSize);
        if (currentPage < totalPages) {
            currentPage++;
            applyFiltersAndRender();
        }
    });

    // Currency Switch Handler
    currencySelect.addEventListener('change', (e) => {
        currencySymbol = e.target.value;
        recalculateSummary();
    });

    // Gather table state and trigger Excel generation
    exportBtn.addEventListener('click', () => {
        exportBtn.disabled = true;
        exportBtn.innerHTML = `
            <svg class="spin" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="2" x2="12" y2="6"></line><line x1="12" y1="18" x2="12" y2="22"></line><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line><line x1="2" y1="12" x2="6" y2="12"></line><line x1="18" y1="12" x2="22" y2="12"></line><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line></svg>
            Generating Excel...
        `;

        // Gather metadata
        const metadata = {
            holder_name: metaHolder.innerText.trim(),
            account_number: metaNumber.innerText.trim(),
            customer_id: metaCustid.innerText.trim(),
            account_type: metaType.innerText.trim(),
            statement_period: metaPeriod.innerText.trim()
        };

        // Gather transactions directly from in-memory state
        const transactions = allTransactions.map(tx => ({
            txn_date: tx.txn_date,
            value_date: tx.value_date,
            particulars: tx.particulars,
            ref_no: tx.ref_no,
            debit: tx.debit,
            credit: tx.credit,
            balance: tx.balance
        }));

        // Post request
        fetch('/api/export', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                metadata,
                transactions,
                currency: currencySymbol
            })
        })
        .then(res => {
            if (!res.ok) {
                return res.json().then(data => { throw new Error(data.error || 'Server error'); });
            }
            return res.json();
        })
        .then(data => {
            if (data.success && data.download_url) {
                showToast('Excel generated! Download starting...', 'success');
                
                // Create temporary link to trigger download
                const link = document.createElement('a');
                link.href = data.download_url;
                link.download = '';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            } else {
                showToast('Failed to export. No download link returned.', 'error');
            }
        })
        .catch(err => {
            showToast(`Export failed: ${err.message}`, 'error');
        })
        .finally(() => {
            exportBtn.disabled = false;
            exportBtn.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                Generate Styled Excel
            `;
        });
    });

    // Toast helper
    function showToast(message, type = 'info') {
        toast.className = `toast ${type}`;
        toastMessage.innerText = message;
        toast.style.display = 'flex';
        
        // Auto-close toast
        if (window.toastTimeout) {
            clearTimeout(window.toastTimeout);
        }
        window.toastTimeout = setTimeout(() => {
            toast.style.display = 'none';
        }, 4000);
    }
});
