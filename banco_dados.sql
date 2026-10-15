-- ==============================================================================
-- SCRIPT DE CRIAÇÃO DO BANCO DE DADOS — DOCENTE360
-- ==============================================================================

-- 1. Tabela de Professores
CREATE TABLE IF NOT EXISTS professores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    departamento VARCHAR(100),
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Tabela de Disciplinas
CREATE TABLE IF NOT EXISTS disciplinas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nome VARCHAR(255) NOT NULL,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Tabela de Turmas
CREATE TABLE IF NOT EXISTS turmas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo VARCHAR(50) UNIQUE NOT NULL,
    curso VARCHAR(100) NOT NULL,
    periodo VARCHAR(50) NOT NULL,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Tabela Principal de Ausências
CREATE TABLE IF NOT EXISTS ausencias (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    professor_id UUID REFERENCES professores(id) ON DELETE CASCADE,
    disciplina_id UUID REFERENCES disciplinas(id) ON DELETE CASCADE,
    turma_id UUID REFERENCES turmas(id) ON DELETE CASCADE,
    data_ausencia DATE NOT NULL,
    horario VARCHAR(50) NOT NULL,
    motivo TEXT,
    status VARCHAR(50) DEFAULT 'Pendente', -- Valores: Pendente, Substituída, Aula Vaga, Aguardando Homologação, Reposta
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Tabela de Substituições
CREATE TABLE IF NOT EXISTS substituicoes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ausencia_id UUID REFERENCES ausencias(id) ON DELETE CASCADE,
    professor_substituto_id UUID REFERENCES professores(id) ON DELETE SET NULL,
    aula_vaga BOOLEAN DEFAULT FALSE,
    observacoes TEXT,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. Tabela de Atestados e Reposições
CREATE TABLE IF NOT EXISTS reposicoes_atestados (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ausencia_id UUID REFERENCES ausencias(id) ON DELETE CASCADE,
    atestado_url TEXT,
    data_reposicao DATE,
    horario_reposicao VARCHAR(50),
    comprovada BOOLEAN DEFAULT FALSE,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 7. Tabela de Usuários Administrativos (Secretaria e Coordenação vinculados ao Supabase Auth)
CREATE TABLE IF NOT EXISTS usuarios (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    perfil VARCHAR(50) NOT NULL CHECK (perfil IN ('Secretaria', 'Coordenador Acadêmico', 'Administrador')),
    cargo VARCHAR(100),
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Habilitar Row Level Security (RLS) para a tabela de usuários
ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;

-- Políticas de segurança
CREATE POLICY "Permitir leitura de usuarios autenticados" 
ON usuarios FOR SELECT 
TO authenticated 
USING (true);

CREATE POLICY "Permitir criacao do proprio usuario" 
ON usuarios FOR INSERT 
TO authenticated 
WITH CHECK (auth.uid() = id);

CREATE POLICY "Permitir atualizacao do proprio usuario" 
ON usuarios FOR UPDATE 
TO authenticated 
USING (auth.uid() = id);

-- Trigger automática para sincronizar novos cadastros do Supabase Auth com a tabela 'usuarios'
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.usuarios (id, email, nome, perfil, cargo)
    VALUES (
        new.id,
        new.email,
        COALESCE(new.raw_user_meta_data->>'nome', split_part(new.email, '@', 1)),
        COALESCE(new.raw_user_meta_data->>'perfil', 'Secretaria'),
        COALESCE(new.raw_user_meta_data->>'cargo', 'Equipe Operacional')
    )
    ON CONFLICT (id) DO UPDATE SET
        nome = EXCLUDED.nome,
        perfil = EXCLUDED.perfil,
        cargo = EXCLUDED.cargo;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ==============================================================================
-- DADOS INICIAIS PARA TESTES (SEEDS)
-- ==============================================================================
INSERT INTO professores (nome, email, departamento) VALUES 
('Carlos Andrade', 'carlos@escola.edu.br', 'Exatas'),
('Mariana Lima', 'mariana@escola.edu.br', 'Humanas'),
('Roberto Silva', 'roberto@escola.edu.br', 'Tecnologia')
ON CONFLICT (email) DO NOTHING;

INSERT INTO disciplinas (codigo, nome) VALUES 
('MAT101', 'Matemática Aplicada'),
('HIS201', 'História Geral'),
('PRG301', 'Programação Python')
ON CONFLICT (codigo) DO NOTHING;

INSERT INTO turmas (codigo, curso, periodo) VALUES 
('T-ENG24', 'Engenharia de Software', 'Matutino'),
('T-ADS24', 'Análise de Sistemas', 'Noturno')
ON CONFLICT (codigo) DO NOTHING;