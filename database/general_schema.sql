-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.access_logs (
  id integer NOT NULL DEFAULT nextval('access_logs_id_seq'::regclass),
  user_id text NOT NULL,
  location_code text NOT NULL,
  timestamp timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT access_logs_pkey PRIMARY KEY (id),
  CONSTRAINT access_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
CREATE TABLE public.asistencias (
  id integer NOT NULL DEFAULT nextval('asistencias_id_seq'::regclass),
  fecha_registro timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  estado text NOT NULL DEFAULT 'Presente'::text,
  dispositivo_info text,
  estudiante_id text NOT NULL,
  clase_id text NOT NULL,
  CONSTRAINT asistencias_pkey PRIMARY KEY (id),
  CONSTRAINT asistencias_estudiante_id_fkey FOREIGN KEY (estudiante_id) REFERENCES public.users(id),
  CONSTRAINT asistencias_clase_id_fkey FOREIGN KEY (clase_id) REFERENCES public.clases(id)
);
CREATE TABLE public.checkins (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  reserva_id uuid NOT NULL,
  usuario_id text NOT NULL,
  usuario_nombre text NOT NULL,
  usuario_email text NOT NULL,
  timestamp timestamp with time zone DEFAULT now(),
  numero_checkin integer NOT NULL,
  estado text DEFAULT 'exitoso'::text CHECK (estado = ANY (ARRAY['exitoso'::text, 'rechazado'::text, 'invalido'::text])),
  mensaje text,
  dispositivo_info text,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT checkins_pkey PRIMARY KEY (id),
  CONSTRAINT fk_checkins_reservas FOREIGN KEY (reserva_id) REFERENCES public.reservas(id),
  CONSTRAINT fk_checkins_usuarios FOREIGN KEY (usuario_id) REFERENCES public.users(id)
);
CREATE TABLE public.clases (
  id text NOT NULL,
  nombre_materia text NOT NULL,
  aula text NOT NULL,
  horario_inicio timestamp without time zone NOT NULL,
  profesor_id text NOT NULL,
  created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT clases_pkey PRIMARY KEY (id),
  CONSTRAINT clases_profesor_id_fkey FOREIGN KEY (profesor_id) REFERENCES public.users(id)
);
CREATE TABLE public.recursos (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  codigo text NOT NULL UNIQUE,
  nombre text NOT NULL,
  descripcion text,
  tipo text NOT NULL CHECK (tipo = ANY (ARRAY['sala_estudio'::text, 'laboratorio'::text, 'modulo_biblioteca'::text, 'parqueadero'::text, 'equipo'::text])),
  ubicacion text NOT NULL,
  capacidad integer DEFAULT 1,
  equipamiento ARRAY,
  estado text DEFAULT 'disponible'::text CHECK (estado = ANY (ARRAY['disponible'::text, 'mantenimiento'::text, 'fuera_servicio'::text])),
  imagen_url text,
  horario_inicio time without time zone DEFAULT '07:00:00'::time without time zone,
  horario_fin time without time zone DEFAULT '21:00:00'::time without time zone,
  dias_disponibles ARRAY DEFAULT '{1,2,3,4,5,6}'::integer[],
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT recursos_pkey PRIMARY KEY (id)
);
CREATE TABLE public.recursos_qr (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  recurso_id uuid NOT NULL,
  codigo_qr text NOT NULL UNIQUE,
  token_secreto text NOT NULL,
  activo boolean DEFAULT true,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT recursos_qr_pkey PRIMARY KEY (id),
  CONSTRAINT fk_recursos_qr_recursos FOREIGN KEY (recurso_id) REFERENCES public.recursos(id)
);
CREATE TABLE public.reservas (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  usuario_id text NOT NULL,
  usuario_nombre text NOT NULL,
  usuario_email text NOT NULL,
  recurso_id uuid NOT NULL,
  fecha date NOT NULL,
  hora_inicio time without time zone NOT NULL,
  hora_fin time without time zone NOT NULL,
  estado text DEFAULT 'confirmada'::text CHECK (estado = ANY (ARRAY['pendiente'::text, 'confirmada'::text, 'en_curso'::text, 'completada'::text, 'cancelada'::text, 'no_show'::text])),
  motivo text,
  num_asistentes_esperados integer DEFAULT 1,
  notas text,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  cancelado_at timestamp with time zone,
  motivo_cancelacion text,
  CONSTRAINT reservas_pkey PRIMARY KEY (id),
  CONSTRAINT fk_reservas_usuarios FOREIGN KEY (usuario_id) REFERENCES public.users(id),
  CONSTRAINT fk_reservas_recursos FOREIGN KEY (recurso_id) REFERENCES public.recursos(id)
);
CREATE TABLE public.tokens_qr (
  id text NOT NULL,
  token_hash text NOT NULL,
  fecha_generacion timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  fecha_expiracion timestamp without time zone NOT NULL,
  clase_id text NOT NULL,
  CONSTRAINT tokens_qr_pkey PRIMARY KEY (id),
  CONSTRAINT tokens_qr_clase_id_fkey FOREIGN KEY (clase_id) REFERENCES public.clases(id)
);
CREATE TABLE public.users (
  id text NOT NULL,
  email text NOT NULL,
  password_hash text NOT NULL,
  full_name text NOT NULL,
  role text NOT NULL DEFAULT 'student'::text,
  created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT users_pkey PRIMARY KEY (id)
);