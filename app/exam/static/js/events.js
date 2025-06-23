// Удаление мероприятия с CSRF-защитой
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            if (confirm('Вы уверены, что хотите удалить это мероприятие?')) {
                const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
                const eventId = this.getAttribute('data-event-id');
                
                fetch(`/events/delete/${eventId}`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'Content-Type': 'application/json'
                    }
                }).then(response => {
                    if (response.ok) {
                        window.location.reload();
                    }
                });
            }
        });
    });
});

fetch(`/events/delete/${eventId}`, {
    method: 'POST',
    headers: {
        'X-CSRFToken': csrfToken,
        'Content-Type': 'application/json'
    }
}).then(response => {
    if (response.ok) {
        window.location.reload();
    } else {
        return response.text().then(text => {
            alert('Ошибка при удалении: ' + text);
        });
    }
}).catch(error => {
    alert('Ошибка сети: ' + error);
});
