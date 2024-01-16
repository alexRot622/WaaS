#![no_std]

use multiversx_sc::types::heap::Vec;

multiversx_sc::imports!();
multiversx_sc::derive_imports!();

#[multiversx_sc::contract]
pub trait WalletContract {
    #[init]
    fn init(&self) {}

    #[endpoint]
    fn upgrade(&self) {}

    #[endpoint]
    fn add_account(&self, account: ManagedBuffer) {
        let mut account_balance = self.account_balance();
        require!(
            account_balance.get(&account).is_none(),
            "Account already exists"
        );
        account_balance.insert(account.clone(), BigUint::from(0u32));
    }

    #[endpoint]
    #[only_owner]
    fn mint(&self, account: ManagedBuffer, amount: BigUint) {
        let mut account_balance = self.account_balance();
        let mut balance = account_balance.get(&account).unwrap_or(BigUint::from(0u32));
        balance += amount.clone();
        account_balance.insert(account.clone(), balance);
        self.history().push(&(
            amount.clone(),
            ManagedBuffer::new_from_bytes("Mint".as_bytes()),
            account.clone(),
        ));
    }

    #[endpoint]
    fn transfer(&self, from: ManagedBuffer, to: ManagedBuffer, amount: BigUint) {
        let mut account_balance = self.account_balance();
        let mut from_balance = account_balance
            .get(&from)
            .expect("From address doesn't exist");
        let mut to_balance = account_balance.get(&to).expect("To address doesn't exist");
        require!(
            from_balance >= amount.clone(),
            "Insufficient balance for transfer"
        );
        from_balance -= amount.clone();
        to_balance += amount.clone();
        account_balance.insert(from.clone(), from_balance);
        account_balance.insert(to.clone(), to_balance);
        self.history()
            .push(&(amount.clone(), from.clone(), to.clone()));
    }

    #[endpoint]
    fn get_account_balance(&self, account: ManagedBuffer) -> BigUint {
        let account_balance = self.account_balance();
        let balance = account_balance.get(&account).unwrap_or(BigUint::from(0u32));
        balance
    }

    #[endpoint]
    fn get_account_history(
        &self,
        account: ManagedBuffer,
    ) -> Vec<(BigUint, ManagedBuffer, ManagedBuffer)> {
        // Get transactions where account is either sender or receiver
        let history = self
            .history()
            .iter()
            .filter(|(_amount, from, to)| from == &account || to == &account)
            .map(|(amount, from, to)| (amount.clone(), from.clone(), to.clone()))
            .collect();
        history
    }

    #[view(getAccountBalance)]
    #[storage_mapper("account_balance")]
    fn account_balance(&self) -> MapMapper<ManagedBuffer, BigUint>;

    #[view(getHistory)]
    #[storage_mapper("history")]
    fn history(&self) -> VecMapper<(BigUint, ManagedBuffer, ManagedBuffer)>;
}
