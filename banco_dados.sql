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
    status VARCHAR(50) DEFAULT 'Pendente', -- Valores: Pendente, Substituída, Aula Vaga, Reposta
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

-- Inserir dados iniciais para testes
INSERT INTO professores (nome, email, departamento) VALUES 
('Carlos Andrade', 'carlos@escola.edu.br', 'Exatas'),
('Mariana Lima', 'mariana@escola.edu.br', 'Humanas'),
('Roberto Silva', 'roberto@escola.edu.br', 'Tecnologia');

INSERT INTO disciplinas (codigo, nome) VALUES 
('MAT101', 'Matemática Aplicada'),
('HIS201', 'História Geral'),
('PRG301', 'Programação Python');

INSERT INTO turmas (codigo, curso, periodo) VALUES 
('T-ENG24', 'Engenharia de Software', 'Matutino'),
('T-ADS24', 'Análise de Sistemas', 'Noturno');