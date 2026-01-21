// Configuración
const API_BASE_URL = 'http://localhost:8000';
let jwtToken = localStorage.getItem('jwt_token') || '';

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    // Cargar token guardado
    document.getElementById('jwt-token').value = jwtToken;
    
    // Configurar formulario de crear ticket
    document.getElementById('form-crear-ticket').addEventListener('submit', crearTicket);
    
    // Cargar catálogos para los selectores
    cargarSelectoresCatalogos();
});

// =============================================
// Utilidades
// =============================================

function setToken() {
    jwtToken = document.getElementById('jwt-token').value.trim();
    localStorage.setItem('jwt_token', jwtToken);
    showToast('Token configurado correctamente', 'success');
}

function getHeaders() {
    const headers = {
        'Content-Type': 'application/json'
    };
    if (jwtToken) {
        headers['Authorization'] = `Bearer ${jwtToken}`;
    }
    return headers;
}

async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
        ...options,
        headers: getHeaders()
    };
    
    try {
        const response = await fetch(url, config);
        const data = response.status !== 204 ? await response.json() : null;
        
        if (!response.ok) {
            throw { status: response.status, data };
        }
        
        return data;
    } catch (error) {
        if (error.data) {
            throw error;
        }
        throw { status: 0, data: { detail: 'Error de conexión con el servidor' } };
    }
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

function showSection(sectionId) {
    // Ocultar todas las secciones
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    
    // Mostrar la sección seleccionada
    document.getElementById(sectionId).classList.add('active');
    event.target.classList.add('active');
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function getPrioridadClass(codigo) {
    const classes = {
        'baja': 'badge-prioridad-baja',
        'media': 'badge-prioridad-media',
        'alta': 'badge-prioridad-alta',
        'critica': 'badge-prioridad-critica'
    };
    return classes[codigo] || 'badge-estado';
}

function showResult(containerId, success, data) {
    const container = document.getElementById(containerId);
    container.className = `result-container ${success ? 'success' : 'error'}`;
    container.innerHTML = success 
        ? `<strong>✅ Operación exitosa</strong><pre>${JSON.stringify(data, null, 2)}</pre>`
        : `<strong>❌ Error</strong><pre>${JSON.stringify(data, null, 2)}</pre>`;
}

// =============================================
// Test de Conexión
// =============================================

async function testConnection() {
    try {
        const data = await apiRequest('/');
        showToast(`Conectado: ${data.message}`, 'success');
    } catch (error) {
        showToast('Error de conexión', 'error');
    }
}

// =============================================
// Catálogos
// =============================================

async function cargarEstados() {
    try {
        const estados = await apiRequest('/tickets/catalogos/estados');
        const container = document.getElementById('estados-list');
        container.innerHTML = estados.map(e => `
            <div class="list-item">
                <span>${e.nombre}</span>
                <span class="badge estado-${e.codigo}">${e.codigo}</span>
            </div>
        `).join('');
        showToast(`${estados.length} estados cargados`, 'success');
    } catch (error) {
        showToast('Error al cargar estados', 'error');
    }
}

async function cargarPrioridades() {
    try {
        const prioridades = await apiRequest('/tickets/catalogos/prioridades');
        const container = document.getElementById('prioridades-list');
        container.innerHTML = prioridades.map(p => `
            <div class="list-item">
                <span>${p.nombre}</span>
                <span class="badge ${getPrioridadClass(p.codigo)}">${p.codigo}</span>
            </div>
        `).join('');
        showToast(`${prioridades.length} prioridades cargadas`, 'success');
    } catch (error) {
        showToast('Error al cargar prioridades', 'error');
    }
}

async function cargarCategorias() {
    try {
        const categorias = await apiRequest('/tickets/catalogos/categorias');
        const container = document.getElementById('categorias-list');
        container.innerHTML = categorias.length 
            ? categorias.map(c => `
                <div class="list-item">
                    <span>${c.nombre}</span>
                    <span class="badge badge-estado">${c.codigo}</span>
                </div>
            `).join('')
            : '<div class="empty-state">No hay categorías</div>';
        showToast(`${categorias.length} categorías cargadas`, 'success');
    } catch (error) {
        showToast('Error al cargar categorías', 'error');
    }
}

async function cargarUbicaciones() {
    try {
        const ubicaciones = await apiRequest('/tickets/catalogos/ubicaciones');
        const container = document.getElementById('ubicaciones-list');
        container.innerHTML = ubicaciones.length 
            ? ubicaciones.map(u => `
                <div class="list-item">
                    <span>${u.nombre}</span>
                    <span class="badge badge-estado">${u.tipo || u.codigo}</span>
                </div>
            `).join('')
            : '<div class="empty-state">No hay ubicaciones</div>';
        showToast(`${ubicaciones.length} ubicaciones cargadas`, 'success');
    } catch (error) {
        showToast('Error al cargar ubicaciones', 'error');
    }
}

async function cargarSelectoresCatalogos() {
    // Cargar estados para filtros
    try {
        const estados = await apiRequest('/tickets/catalogos/estados');
        const selectEstado = document.getElementById('filter-estado');
        estados.forEach(e => {
            selectEstado.innerHTML += `<option value="${e.codigo}">${e.nombre}</option>`;
        });
    } catch (e) {}
    
    // Cargar prioridades para filtros
    try {
        const prioridades = await apiRequest('/tickets/catalogos/prioridades');
        const selectPrioridad = document.getElementById('filter-prioridad');
        prioridades.forEach(p => {
            selectPrioridad.innerHTML += `<option value="${p.codigo}">${p.nombre}</option>`;
        });
    } catch (e) {}
    
    // Cargar categorías para filtros y formulario
    try {
        const categorias = await apiRequest('/tickets/catalogos/categorias');
        const selectCategoria = document.getElementById('filter-categoria');
        const selectCategoriaForm = document.getElementById('categoria');
        categorias.forEach(c => {
            selectCategoria.innerHTML += `<option value="${c.codigo}">${c.nombre}</option>`;
            selectCategoriaForm.innerHTML += `<option value="${c.codigo}">${c.nombre}</option>`;
        });
    } catch (e) {}
    
    // Cargar ubicaciones para formulario
    try {
        const ubicaciones = await apiRequest('/tickets/catalogos/ubicaciones');
        const selectUbicacion = document.getElementById('ubicacion');
        ubicaciones.forEach(u => {
            selectUbicacion.innerHTML += `<option value="${u.codigo}">${u.nombre}</option>`;
        });
    } catch (e) {}
}

// =============================================
// Tickets - Listar
// =============================================

async function cargarTickets() {
    const params = new URLSearchParams();
    
    const estado = document.getElementById('filter-estado').value;
    const prioridad = document.getElementById('filter-prioridad').value;
    const categoria = document.getElementById('filter-categoria').value;
    const limit = document.getElementById('filter-limit').value;
    const offset = document.getElementById('filter-offset').value;
    
    if (estado) params.append('estado_codigo', estado);
    if (prioridad) params.append('prioridad_codigo', prioridad);
    if (categoria) params.append('categoria_codigo', categoria);
    if (limit) params.append('limit', limit);
    if (offset) params.append('offset', offset);
    
    try {
        const response = await apiRequest(`/tickets/?${params.toString()}`);
        renderTickets(response);
        showToast(`${response.incidencias.length} tickets encontrados`, 'success');
    } catch (error) {
        document.getElementById('tickets-list').innerHTML = 
            `<div class="empty-state">Error al cargar tickets: ${error.data?.detail || 'Error desconocido'}</div>`;
        showToast('Error al cargar tickets', 'error');
    }
}

function renderTickets(response) {
    const container = document.getElementById('tickets-list');
    const paginationInfo = document.getElementById('pagination-info');
    
    if (!response.incidencias || response.incidencias.length === 0) {
        container.innerHTML = '<div class="empty-state">No hay tickets que mostrar</div>';
        paginationInfo.innerHTML = '';
        return;
    }
    
    container.innerHTML = response.incidencias.map(ticket => `
        <div class="ticket-card" onclick="verDetalleTicket(${ticket.id})">
            <div class="ticket-header">
                <span class="ticket-id">#${ticket.id}</span>
                <span class="badge estado-${ticket.estado.codigo}">${ticket.estado.nombre}</span>
            </div>
            <div class="ticket-title">${ticket.titulo}</div>
            <div class="ticket-meta">
                <span>📁 ${ticket.categoria?.nombre || 'Sin categoría'}</span>
                <span class="badge ${getPrioridadClass(ticket.prioridad.codigo)}">${ticket.prioridad.nombre}</span>
                <span>👤 ${ticket.reportante?.full_name || ticket.reportante?.email || 'Anónimo'}</span>
                <span>📅 ${formatDate(ticket.fecha_creacion)}</span>
            </div>
        </div>
    `).join('');
    
    paginationInfo.innerHTML = `
        Mostrando ${response.incidencias.length} de ${response.total} tickets 
        | Página ${Math.floor(response.offset / response.limit) + 1}
        ${response.has_more ? ' | <button class="btn btn-secondary" onclick="siguientePagina()">Siguiente →</button>' : ''}
    `;
}

function siguientePagina() {
    const offsetInput = document.getElementById('filter-offset');
    const limitInput = document.getElementById('filter-limit');
    offsetInput.value = parseInt(offsetInput.value) + parseInt(limitInput.value);
    cargarTickets();
}

function verDetalleTicket(ticketId) {
    document.getElementById('ticket-id-buscar').value = ticketId;
    showSection('detalle-ticket');
    document.querySelectorAll('.tab')[3].classList.add('active');
    document.querySelectorAll('.tab').forEach((t, i) => {
        if (i !== 3) t.classList.remove('active');
    });
    buscarTicket();
}

// =============================================
// Tickets - Crear
// =============================================

async function crearTicket(event) {
    event.preventDefault();
    
    const ticketData = {
        titulo: document.getElementById('titulo').value,
        descripcion: document.getElementById('descripcion').value,
        prioridad_codigo: document.getElementById('prioridad').value
    };
    
    const categoria = document.getElementById('categoria').value;
    const ubicacion = document.getElementById('ubicacion').value;
    
    if (categoria) ticketData.categoria_codigo = categoria;
    if (ubicacion) ticketData.ubicacion_codigo = ubicacion;
    
    try {
        const ticket = await apiRequest('/tickets/', {
            method: 'POST',
            body: JSON.stringify(ticketData)
        });
        
        showResult('crear-resultado', true, ticket);
        showToast(`Ticket #${ticket.id} creado exitosamente`, 'success');
        
        // Limpiar formulario
        document.getElementById('form-crear-ticket').reset();
    } catch (error) {
        showResult('crear-resultado', false, error.data);
        showToast('Error al crear ticket', 'error');
    }
}

// =============================================
// Tickets - Detalle
// =============================================

let ticketActual = null;

async function buscarTicket() {
    const ticketId = document.getElementById('ticket-id-buscar').value;
    
    if (!ticketId) {
        showToast('Ingresa un ID de ticket', 'error');
        return;
    }
    
    try {
        const ticket = await apiRequest(`/tickets/${ticketId}`);
        ticketActual = ticket;
        renderTicketDetalle(ticket);
        
        // Mostrar secciones adicionales
        document.getElementById('historial-section').style.display = 'block';
        document.getElementById('comentarios-section').style.display = 'block';
        
        showToast(`Ticket #${ticket.id} cargado`, 'success');
    } catch (error) {
        document.getElementById('ticket-detalle').innerHTML = 
            `<div class="empty-state">Ticket no encontrado o sin acceso</div>`;
        document.getElementById('historial-section').style.display = 'none';
        document.getElementById('comentarios-section').style.display = 'none';
        showToast('Error al buscar ticket', 'error');
    }
}

function renderTicketDetalle(ticket) {
    const container = document.getElementById('ticket-detalle');
    container.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <h3>Ticket #${ticket.id}</h3>
            <span class="badge estado-${ticket.estado.codigo}" style="font-size: 1rem; padding: 0.5rem 1rem;">
                ${ticket.estado.nombre}
            </span>
        </div>
        
        <h4 style="margin-bottom: 1rem;">${ticket.titulo}</h4>
        <p style="margin-bottom: 1.5rem; padding: 1rem; background: #f5f6fa; border-radius: 8px;">
            ${ticket.descripcion}
        </p>
        
        <div class="detail-grid">
            <div class="detail-item">
                <div class="detail-label">Prioridad</div>
                <div class="detail-value">
                    <span class="badge ${getPrioridadClass(ticket.prioridad.codigo)}">${ticket.prioridad.nombre}</span>
                </div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Categoría</div>
                <div class="detail-value">${ticket.categoria?.nombre || 'Sin categoría'}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Ubicación</div>
                <div class="detail-value">${ticket.ubicacion?.nombre || 'Sin ubicación'}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Reportante</div>
                <div class="detail-value">${ticket.reportante?.full_name || ticket.reportante?.email || 'N/A'}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Responsable</div>
                <div class="detail-value">${ticket.responsable?.full_name || ticket.responsable?.email || 'Sin asignar'}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Fecha Creación</div>
                <div class="detail-value">${formatDate(ticket.fecha_creacion)}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Última Actualización</div>
                <div class="detail-value">${formatDate(ticket.fecha_actualizacion)}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Fecha Resolución</div>
                <div class="detail-value">${formatDate(ticket.fecha_resolucion)}</div>
            </div>
        </div>
    `;
}

// =============================================
// Historial
// =============================================

async function cargarHistorial() {
    if (!ticketActual) {
        showToast('Primero busca un ticket', 'error');
        return;
    }
    
    try {
        const historial = await apiRequest(`/tickets/${ticketActual.id}/historial`);
        renderHistorial(historial);
        showToast(`${historial.length} registros en historial`, 'success');
    } catch (error) {
        document.getElementById('historial-list').innerHTML = 
            `<div class="empty-state">Error al cargar historial</div>`;
        showToast('Error al cargar historial', 'error');
    }
}

function renderHistorial(historial) {
    const container = document.getElementById('historial-list');
    
    if (!historial.length) {
        container.innerHTML = '<div class="empty-state">No hay historial</div>';
        return;
    }
    
    container.innerHTML = historial.map(h => `
        <div class="historial-item">
            <div class="historial-fecha">${formatDate(h.fecha_cambio)}</div>
            <div class="historial-accion">${h.accion}</div>
            <div>${h.descripcion || ''}</div>
            ${h.valor_anterior || h.valor_nuevo ? `
                <div style="font-size: 0.85rem; color: #666; margin-top: 0.5rem;">
                    ${h.valor_anterior ? `<span>Antes: ${h.valor_anterior}</span>` : ''}
                    ${h.valor_nuevo ? `<span> → Después: ${h.valor_nuevo}</span>` : ''}
                </div>
            ` : ''}
            <div style="font-size: 0.8rem; color: #999;">Por: ${h.usuario?.full_name || h.usuario?.email || 'Sistema'}</div>
        </div>
    `).join('');
}

// =============================================
// Comentarios
// =============================================

async function cargarComentarios() {
    if (!ticketActual) {
        showToast('Primero busca un ticket', 'error');
        return;
    }
    
    try {
        const comentarios = await apiRequest(`/tickets/${ticketActual.id}/comentarios?incluir_internos=true`);
        renderComentarios(comentarios);
        showToast(`${comentarios.length} comentarios cargados`, 'success');
    } catch (error) {
        document.getElementById('comentarios-list').innerHTML = 
            `<div class="empty-state">Error al cargar comentarios</div>`;
        showToast('Error al cargar comentarios', 'error');
    }
}

function renderComentarios(comentarios) {
    const container = document.getElementById('comentarios-list');
    
    if (!comentarios.length) {
        container.innerHTML = '<div class="empty-state">No hay comentarios</div>';
        return;
    }
    
    container.innerHTML = comentarios.map(c => `
        <div class="comentario-item ${c.es_interno ? 'interno' : ''}">
            <div class="comentario-autor">
                ${c.usuario?.full_name || c.usuario?.email || 'Usuario'}
                ${c.es_interno ? '<span class="badge badge-prioridad-alta">Interno</span>' : ''}
            </div>
            <div class="comentario-fecha">${formatDate(c.fecha_creacion)}</div>
            <div style="margin-top: 0.5rem;">${c.contenido}</div>
        </div>
    `).join('');
}

async function agregarComentario() {
    if (!ticketActual) {
        showToast('Primero busca un ticket', 'error');
        return;
    }
    
    const contenido = document.getElementById('nuevo-comentario').value.trim();
    const esInterno = document.getElementById('comentario-interno').checked;
    
    if (!contenido) {
        showToast('Escribe un comentario', 'error');
        return;
    }
    
    try {
        await apiRequest(`/tickets/${ticketActual.id}/comentarios`, {
            method: 'POST',
            body: JSON.stringify({
                contenido,
                es_interno: esInterno
            })
        });
        
        showToast('Comentario agregado', 'success');
        document.getElementById('nuevo-comentario').value = '';
        document.getElementById('comentario-interno').checked = false;
        cargarComentarios();
    } catch (error) {
        showToast(`Error: ${error.data?.detail || 'Error al agregar comentario'}`, 'error');
    }
}

// =============================================
// Acciones sobre Tickets
// =============================================

async function cambiarEstado() {
    const ticketId = document.getElementById('action-ticket-id-estado').value;
    const estadoCodigo = document.getElementById('nuevo-estado').value;
    const comentario = document.getElementById('comentario-estado').value;
    
    if (!ticketId) {
        showToast('Ingresa un ID de ticket', 'error');
        return;
    }
    
    try {
        const result = await apiRequest(`/tickets/${ticketId}/cambiar-estado`, {
            method: 'POST',
            body: JSON.stringify({
                estado_codigo: estadoCodigo,
                comentario: comentario || null
            })
        });
        
        showResult('resultado-cambiar-estado', true, result);
        showToast('Estado cambiado exitosamente', 'success');
    } catch (error) {
        showResult('resultado-cambiar-estado', false, error.data);
        showToast('Error al cambiar estado', 'error');
    }
}

async function asignarResponsable() {
    const ticketId = document.getElementById('action-ticket-id-asignar').value;
    const responsableId = document.getElementById('responsable-id').value;
    const comentario = document.getElementById('comentario-asignar').value;
    
    if (!ticketId || !responsableId) {
        showToast('Completa todos los campos requeridos', 'error');
        return;
    }
    
    try {
        const result = await apiRequest(`/tickets/${ticketId}/asignar`, {
            method: 'POST',
            body: JSON.stringify({
                responsable_id: responsableId,
                comentario: comentario || null
            })
        });
        
        showResult('resultado-asignar', true, result);
        showToast('Responsable asignado exitosamente', 'success');
    } catch (error) {
        showResult('resultado-asignar', false, error.data);
        showToast('Error al asignar responsable', 'error');
    }
}

async function actualizarTicket() {
    const ticketId = document.getElementById('action-ticket-id-actualizar').value;
    const titulo = document.getElementById('update-titulo').value.trim();
    const descripcion = document.getElementById('update-descripcion').value.trim();
    const prioridad = document.getElementById('update-prioridad').value;
    
    if (!ticketId) {
        showToast('Ingresa un ID de ticket', 'error');
        return;
    }
    
    const updateData = {};
    if (titulo) updateData.titulo = titulo;
    if (descripcion) updateData.descripcion = descripcion;
    if (prioridad) updateData.prioridad_codigo = prioridad;
    
    if (Object.keys(updateData).length === 0) {
        showToast('No hay cambios para actualizar', 'error');
        return;
    }
    
    try {
        const result = await apiRequest(`/tickets/${ticketId}`, {
            method: 'PUT',
            body: JSON.stringify(updateData)
        });
        
        showResult('resultado-actualizar', true, result);
        showToast('Ticket actualizado exitosamente', 'success');
    } catch (error) {
        showResult('resultado-actualizar', false, error.data);
        showToast('Error al actualizar ticket', 'error');
    }
}

async function eliminarTicket() {
    const ticketId = document.getElementById('action-ticket-id-eliminar').value;
    
    if (!ticketId) {
        showToast('Ingresa un ID de ticket', 'error');
        return;
    }
    
    if (!confirm(`¿Estás seguro de eliminar el ticket #${ticketId}? Esta acción no se puede deshacer.`)) {
        return;
    }
    
    try {
        await apiRequest(`/tickets/${ticketId}`, {
            method: 'DELETE'
        });
        
        showResult('resultado-eliminar', true, { message: `Ticket #${ticketId} eliminado` });
        showToast('Ticket eliminado exitosamente', 'success');
    } catch (error) {
        showResult('resultado-eliminar', false, error.data);
        showToast('Error al eliminar ticket', 'error');
    }
}
