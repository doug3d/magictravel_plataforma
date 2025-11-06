from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.configuration import configure_db, configure_routes
from src.seed import seed_database


def create_lifespan(run_seed=True):
    """
    Cria o context manager de lifespan.
    """
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """
        Gerencia o ciclo de vida da aplicação.
        Executa seed do banco de dados no startup.
        """
        # Startup: executar seed (apenas em produção/dev, não em testes)
        if run_seed:
            try:
                await seed_database()
            except Exception as e:
                print(f"⚠️  Erro ao executar seed: {e}")
        
        yield
        
        # Shutdown: cleanup se necessário
        pass
    
    return lifespan


def create_application(fake_db=False):
    # Não executar seed em testes (fake_db=True)
    lifespan = create_lifespan(run_seed=not fake_db)
    app = FastAPI(lifespan=lifespan)

    configure_db(app, fake_db)
    configure_routes(app)

    return app

app = create_application()
